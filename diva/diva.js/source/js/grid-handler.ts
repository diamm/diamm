import { maxBy } from './utils/maxby';
import ViewerCore from './viewer-core';
import {
    Dimension,
    LayoutGroupPage,
    Offset,
    PageGroup,
    Region,
    ViewportSize
} from "./viewer-type-definitions";
import DocumentLayout from "./document-layout";

export default class GridHandler
{
    _viewerCore: ViewerCore;

    constructor (viewerCore: ViewerCore)
    {
        this._viewerCore = viewerCore;
    }

    // USER EVENTS
    onDoubleClick (_event: MouseEvent, coords: Offset)
    {
        const position = this._viewerCore.getPagePositionAtViewportOffset(coords);

        const layout = this._viewerCore.getCurrentLayout()!;
        const viewport: ViewportSize = this._viewerCore.getViewport();
        const pageToViewportCenterOffset = layout.getPageToViewportCenterOffset(position.anchorPage, viewport)!;

        this._viewerCore.reload({
            inGrid: false,
            goDirectlyTo: position.anchorPage,
            horizontalOffset: pageToViewportCenterOffset.x + position.offset.left,
            verticalOffset: pageToViewportCenterOffset.y + position.offset.top
        });
    }

    onPinch ()
    {
        this._viewerCore.reload({inGrid: false});
    }

    // VIEW EVENTS
    onViewWillLoad ()
    {
        // FIXME(wabain): Should something happen here?
        /* No-op */
    }

    onViewDidLoad ()
    {
        // FIXME(wabain): Should something happen here?
        /* No-op */
    }

    onViewDidUpdate (renderedPages: number[], targetPage: number | null)
    {
        // return early if there are no rendered pages in view.
        if (renderedPages.length === 0)
        {
            return;
        }

        // calculate the visible pages from the rendered pages
        let temp = this._viewerCore.viewerState.viewport.intersectionTolerance;
        // without setting to 0, isPageVisible returns true for pages out of viewport by intersectionTolerance
        this._viewerCore.viewerState.viewport.intersectionTolerance = 0;
        let visiblePages = renderedPages.filter((index: number) => this._viewerCore.viewerState.renderer!.isPageVisible(index));
        // reset back to original value after getting true visible pages
        this._viewerCore.viewerState.viewport.intersectionTolerance = temp;

        if (targetPage !== null)
        {
            this._viewerCore.setCurrentPages(targetPage, visiblePages);
            return;
        }

        // Select the current page from the first row if it is fully visible, or from
        // the second row if it is fully visible, or from the centermost row otherwise.
        // If the current page is in that group then don't change it. Otherwise, set
        // the current page to the group's first page.

        const layout: DocumentLayout = this._viewerCore.getCurrentLayout()!;
        const groups: PageGroup[] = [];

        renderedPages.forEach((pageIndex: number) =>
        {
            const group: PageGroup = layout.getPageInfo(pageIndex)!.group;
            if (groups.length === 0 || group !== groups[groups.length - 1])
            {
                groups.push(group);
            }
        });

        const viewport = this._viewerCore.getViewport();
        let chosenGroup;

        if (groups.length === 1 || groups[0].region.top >= viewport.top)
        {
            chosenGroup = groups[0];
        }
        else if (groups[1].region.bottom <= viewport.bottom)
        {
            chosenGroup = groups[1];
        }
        else
        {
            chosenGroup = getCentermostGroup(groups, viewport);
        }

        const currentPage = this._viewerCore.getSettings().activePageIndex;

        const hasCurrentPage = chosenGroup.pages.some((page: LayoutGroupPage) => page.index === currentPage);

        if (!hasCurrentPage)
        {
            this._viewerCore.setCurrentPages(chosenGroup.pages[0].index, visiblePages);
        }
    }

    destroy ()
    {
        // No-op
    }
}

function getCentermostGroup (groups: any[] | null, viewport: Region & Dimension)
{
    const viewportMiddle = viewport.top + viewport.height / 2;

    return maxBy(groups, group =>
    {
        const groupMiddle = group.region.top + group.dimensions.height / 2;
        return -Math.abs(viewportMiddle - groupMiddle);
    });
}
