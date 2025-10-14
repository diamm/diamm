import {ActiveViewOptions, MergedConfiguration, Options, OptionsValidator, ValidationOptions} from "./options-settings";

export default class ValidationRunner
{
    whitelistedKeys: Array<any>;
    additionalProperties: Array<any>;
    validations: OptionsValidator[];

    constructor(options: ValidationOptions)
    {
        this.whitelistedKeys = options.whitelistedKeys || [];
        this.additionalProperties = options.additionalProperties || [];
        this.validations = options.validations;
    }

    isValid(key: string, value: any, settings: Options): boolean
    {
        // Get the validation index
        let validationIndex = null;

        this.validations.some((validation: { key: string; }, index: any): boolean =>
        {
            if (validation.key !== key)
            {
                return false;
            }

            validationIndex = index;
            return true;
        });

        if (validationIndex === null)
        {
            return true;
        }

        // Run the validation
        const dummyChanges: Record<string, any> = {};
        dummyChanges[key] = value;
        const proxier = createSettingsProxier(settings, dummyChanges, this);

        return !this._runValidation(validationIndex, value, proxier);
    }

    validate(settings: Options)
    {
        this._validateOptions({}, settings);
    }

    getValidatedOptions(settings: MergedConfiguration, options: ActiveViewOptions): ActiveViewOptions
    {
        const cloned = Object.assign({}, options);
        this._validateOptions(settings, cloned);
        return cloned;
    }

    _validateOptions (settings: any, options: ActiveViewOptions)
    {
        const settingsProxier = createSettingsProxier(settings, options, this);
        this._applyValidations(options, settingsProxier);
    }

    _applyValidations (options: ActiveViewOptions, proxier: { proxy: {}; index: null; })
    {
        this.validations.forEach((validation: { key: PropertyKey; }, index: any) =>
        {
            if (!options.hasOwnProperty(validation.key))
            {
                return;
            }

            const input = options[validation.key];
            const corrected = this._runValidation(index, input, proxier);

            if (corrected)
            {
                if (!corrected.warningSuppressed)
                {
                    emitWarning(validation.key, input, corrected.value);
                }

                options[validation.key] = corrected.value;
            }
        }, this);
    }

    _runValidation (index: string | number, input: any, proxier: { proxy: any; index: any; })
    {
        const validation = this.validations[index];

        proxier.index = index;

        let warningSuppressed = false;
        const config = {
            suppressWarning: () =>
            {
                warningSuppressed = true;
            }
        };

        const outputValue = validation.validate(input, proxier.proxy, config);

        if (outputValue === undefined || outputValue === input)
        {
            return null;
        }

        return {
            value: outputValue,
            warningSuppressed: warningSuppressed
        };
    }
}

// @ts-ignore
// @ts-ignore
/**
 * The settings proxy wraps the settings object and ensures that
 * only values which have previously been validated are accessed,
 * throwing a TypeError otherwise.
 *
 * FIXME(wabain): Is it worth keeping this? When I wrote it I had
 * multiple validation stages and it was a lot harder to keep track
 * of everything, so this was more valuable.
 */
function createSettingsProxier (settings: any, options: ActiveViewOptions | Record<string, any>, runner: ValidationRunner)
{
    const proxier = {
        proxy: {},
        index: null
    };

    const lookup = lookupValue.bind(null, settings, options);

    const properties = {};

    runner.whitelistedKeys.forEach((whitelisted: string | number) =>
    {
        properties[whitelisted] = {
            get: lookup.bind(null, whitelisted)
        };
    });

    runner.additionalProperties.forEach((additional: { key: string | number; get: any; }) =>
    {
        properties[additional.key] = {
            get: additional.get
        };
    });

    runner.validations.forEach( (validation: { key: string; }, validationIndex: number) =>
    {
        properties[validation.key] = {
            get: () =>
            {
                if (validationIndex < proxier.index)
                {
                    return lookup(validation.key);
                }

                const currentKey = runner.validations[proxier.index].key;
                throw new TypeError('Cannot access setting ' + validation.key + ' while validating ' + currentKey);
            }
        };
    });

    Object.defineProperties(proxier.proxy, properties);

    return proxier;
}

function emitWarning (key: PropertyKey, original: string, corrected: string)
{
    console.warn('Invalid value for ' + (key as string) + ': ' + original + '. Using ' + corrected + ' instead.');
}

function lookupValue (base: { [x: string]: any; }, extension: { [x: string]: any; }, key: string)
{
    if (key in extension)
    {
        return extension[key];
    }

    return base[key];
}
