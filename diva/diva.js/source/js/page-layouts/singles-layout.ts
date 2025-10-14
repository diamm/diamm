import getPageDimensions from './page-dimensions';
import {LayoutGroupSettings} from "../options-settings";
import {Dimension, DivaPage, LayoutGroupPages} from "../viewer-type-definitions";

export default function getSinglesLayoutGroups (viewerConfig: LayoutGroupSettings): LayoutGroupPages[]
{
    const manifest = viewerConfig.manifest;

    // Render each page alone in a group
    const pages: LayoutGroupPages[] = [];
    manifest.pages.forEach( (page: DivaPage, index: number) =>
    {
        if (!viewerConfig.showNonPagedPages && manifest.paged && !page.paged)
        {
            return;
        }

        const pageDims: Dimension = getPageDimensions(index, manifest);

        pages.push({
            dimensions: pageDims,
            pages: [{
                index: index,
                groupOffset: { top: 0, left: 0 },
                dimensions: pageDims
            }]
        });
    });

    return pages;
}
