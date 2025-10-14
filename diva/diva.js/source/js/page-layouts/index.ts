import getBookLayoutGroups from './book-layout';
import getSinglesLayoutGroups from './singles-layout';
import getGridLayoutGroups from './grid-layout';
import {LayoutGroupSettings, MergedConfiguration} from "../options-settings";
import {LayoutGroupPages} from "../viewer-type-definitions";

/** Get the relative positioning of pages for the current view */
export default function getPageLayouts (settings: MergedConfiguration): LayoutGroupPages[]
{
    if (settings.inGrid)
    {
        return getGridLayoutGroups(pluck(settings, [
            'manifest',
            'viewport',
            'pagesPerRow',
            'fixedHeightGrid',
            'fixedPadding',
            'showNonPagedPages'
        ]));
    }
    else
    {
        const config: LayoutGroupSettings = pluck(settings, ['manifest', 'verticallyOriented', 'showNonPagedPages']);

        if (settings.inBookLayout)
        {
            return getBookLayoutGroups(config);
        }
        else
        {
            return getSinglesLayoutGroups(config);
        }
    }
}

function pluck (obj: MergedConfiguration, keys: string[]): LayoutGroupSettings
{
    const out: LayoutGroupSettings = {};
    keys.forEach(function (key)
    {
        out[key] = obj[key];
    });
    return out;
}
