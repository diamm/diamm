import getPageDimensions from './page-dimensions';
import {LayoutGroupSettings} from "../options-settings";
import {BookLayoutPage, DivaPage, LayoutGroupPages} from "../viewer-type-definitions";

export default function getBookLayoutGroups (viewerConfig: LayoutGroupSettings): LayoutGroupPages[]
{
    const groupings = getGroupings(viewerConfig);

    return groupings.map(grouping => getGroupLayoutsFromPageGrouping(viewerConfig, grouping));
}

function getGroupings(viewerConfig: LayoutGroupSettings)
{
    const manifest = viewerConfig.manifest;

    const pagesByGroup: any[] = [];
    let leftPage: BookLayoutPage | null = null;
    let nonPagedPages: BookLayoutPage[] = []; // Pages to display below the current group

    const _addNonPagedPages = () =>
    {
        for (let i = 0, nlen = nonPagedPages.length; i < nlen; i++)
        {
            pagesByGroup.push([ nonPagedPages[i] ]);
        }
        nonPagedPages = [];
    };

    manifest.pages.forEach( (page: DivaPage, index: number) =>
    {
        const pageRecord: BookLayoutPage = {
            index: index,
            dimensions: getPageDimensions(index, manifest),
            paged: (!manifest.paged || page.paged)
        };

        // Only display non-paged pages if specified in the settings
        if (!viewerConfig.showNonPagedPages && !pageRecord.paged)
        {
            return;
        }

        if (!pageRecord.paged)
        {
            nonPagedPages.push(pageRecord);
        }
        else if (index === 0 || page.facingPages)
        {
            // The first page is placed on its own
            pagesByGroup.push([pageRecord]);
            _addNonPagedPages();
        }
        else if (leftPage === null)
        {
            leftPage = pageRecord;
        }
        else
        {
            pagesByGroup.push([leftPage, pageRecord]);
            leftPage = null;
            _addNonPagedPages();
        }
    });

    // Flush a final left page
    if (leftPage !== null)
    {
        pagesByGroup.push([leftPage]);
        _addNonPagedPages();
    }

    return pagesByGroup;
}

function getGroupLayoutsFromPageGrouping(viewerConfig: LayoutGroupSettings, grouping: string | any[]): LayoutGroupPages
{
    const verticallyOriented = viewerConfig.verticallyOriented;

    if (grouping.length === 2)
    {
        return getFacingPageGroup(grouping[0], grouping[1], verticallyOriented);
    }

    const page = grouping[0];
    const pageDims = page.dimensions;

    // The first page is placed on its own to the right in vertical orientation.
    // NB that this needs to be the page with index 0; if the first page is excluded
    // from the layout then this special case shouldn't apply.
    // If the page is tagged as 'non-paged', center it horizontally
    let leftOffset;
    if (page.paged)
    {
        leftOffset = (page.index === 0 && verticallyOriented) ? pageDims.width : 0;
    }
    else
    {
        leftOffset = (verticallyOriented) ? pageDims.width / 2 : 0;
    }

    const shouldBeHorizontallyAdjusted =
        verticallyOriented && !viewerConfig.manifest.pages[page.index].facingPages;

    // We need to left-align the page in vertical orientation, so we double
    // the group width
    return {
        dimensions: {
            height: pageDims.height,
            width: shouldBeHorizontallyAdjusted ? pageDims.width * 2 : pageDims.width
        },
        pages: [{
            index: page.index,
            groupOffset: {
                top: 0,
                left: leftOffset
            },
            dimensions: pageDims
        }]
    };
}

function getFacingPageGroup(leftPage: { dimensions: any; index: any; }, rightPage: {
    dimensions: any;
    index: any;
}, verticallyOriented: any): LayoutGroupPages
{
    const leftDims = leftPage.dimensions;
    const rightDims = rightPage.dimensions;

    const height = Math.max(leftDims.height, rightDims.height);

    let width, firstLeftOffset, secondLeftOffset;

    if (verticallyOriented)
    {
        const midWidth = Math.max(leftDims.width, rightDims.width);

        width = midWidth * 2;

        firstLeftOffset = midWidth - leftDims.width;
        secondLeftOffset = midWidth;
    }
    else
    {
        width = leftDims.width + rightDims.width;
        firstLeftOffset = 0;
        secondLeftOffset = leftDims.width;
    }

    return {
        dimensions: {
            height: height,
            width: width
        },
        pages: [
            {
                index: leftPage.index,
                dimensions: leftDims,
                groupOffset: {
                    top: 0,
                    left: firstLeftOffset
                }
            },
            {
                index: rightPage.index,
                dimensions: rightDims,
                groupOffset: {
                    top: 0,
                    left: secondLeftOffset
                }
            }
        ]
    };
}
