// TODO: requestAnimationFrame fallback

import {AnimationOptions} from "./viewer-type-definitions";

export default {
    animate,
    easing: {
        linear: linearEasing,
        cubic: inOutCubicEasing
    }
};

let now: (() => number) = (): number => { return performance.now(); };


function animate (options: AnimationOptions)
{
    const durationMs = options.duration;
    const parameters = options.parameters;
    const onUpdate = options.onUpdate;
    const onEnd = options.onEnd;

    // Setup
    // Times are in milliseconds from a basically arbitrary start
    const start = now();
    const end = start + durationMs;

    const tweenFns = {};
    const values = {};
    const paramKeys: string[] = Object.keys(parameters);

    paramKeys.forEach((key: string) => {
        const config = parameters[key];
        tweenFns[key] = interpolate(config.from, config.to, config.easing || inOutCubicEasing);
    });

    // Run it!
    let requestId: number | null = requestAnimationFrame(update);

    return {
        cancel()
        {
            if (requestId !== null)
            {
                cancelAnimationFrame(requestId);
                handleAnimationCompletion({
                    interrupted: true
                });
            }
        }
    };

    function update()
    {
        const current: number = now();
        const elapsed: number = Math.min((current - start) / durationMs, 1);

        updateValues(elapsed);
        onUpdate(values);

        if (current < end)
        {
            requestId = requestAnimationFrame(update);
        }
        else
        {
            handleAnimationCompletion({
                interrupted: false
            });
        }
    }

    function updateValues(elapsed: number)
    {
        paramKeys.forEach(key => {
            values[key] = tweenFns[key](elapsed);
        });
    }

    function handleAnimationCompletion(info: { interrupted: boolean; })
    {
        requestId = null;

        if (onEnd)
        {
            onEnd(info);
        }
    }
}

function interpolate(start: any, end: any, easing: any)
{
    return (elapsed: any) => { return start + (end - start) * easing(elapsed); };
}

/**
 * Easing functions. inOutCubicEasing is the default, but
 * others are given for convenience.
 *
 **/
function linearEasing(e: number): number
{
    return e;
}

/* jshint ignore:start */
function inOutQuadEasing (e: number): number
{
    return e < .5 ? 2 * e * e : -1+(4-2 * e) * e
}
/* jshint ignore:end */


function inOutCubicEasing (t: number): number
{
    return t < 0.5 ? 4 * t * t * t : ( t - 1 ) * ( 2 * t - 2 ) * ( 2 * t - 2 ) + 1;
}
