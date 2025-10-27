/**
 * Manages a collection of page overlays, which implement a low-level
 * API for synchronizing HTML pages to the canvas. Each overlay needs
 * to implement the following protocol:
 *
 *   mount(): Called when a page is first rendered
 *   refresh(): Called when a page is moved
 *   unmount(): Called when a previously rendered page has stopped being rendered
 *
 * @class
 */
import PageToolsOverlay from "./page-tools-overlay";

export default class PageOverlayManager
{
    _pages: Record<number, any[]>;
    _renderedPages: any[];
    _renderedPageMap: Record<number, any>;

    constructor ()
    {
        this._pages = {};
        this._renderedPages = [];
        this._renderedPageMap = {};
    }

    addOverlay (overlay: PageToolsOverlay)
    {
        const overlaysByPage = this._pages[overlay.page] || (this._pages[overlay.page] = []);

        overlaysByPage.push(overlay);

        if (this._renderedPageMap[overlay.page])
        {
            overlay.mount();
        }
    }

    removeOverlay (overlay: PageToolsOverlay)
    {
        const page = overlay.page;
        const overlaysByPage = this._pages[page];

        if (!overlaysByPage)
        {
            return;
        }

        const overlayIndex = overlaysByPage.indexOf(overlay);

        if (overlayIndex === -1)
        {
            return;
        }

        if (this._renderedPageMap[page])
        {
            overlaysByPage[overlayIndex].unmount();
        }

        overlaysByPage.splice(overlayIndex, 1);

        if (overlaysByPage.length === 0)
        {
            delete this._pages[page];
        }
    }

    updateOverlays (renderedPages: number[])
    {
        const previouslyRendered = this._renderedPages;
        const newRenderedMap: Record<number, boolean> = {};

        renderedPages.map( (pageIndex: number) =>
        {
            newRenderedMap[pageIndex] = true;

            if (!this._renderedPageMap[pageIndex])
            {
                this._renderedPageMap[pageIndex] = true;

                this._invokeOnOverlays(pageIndex, (overlay: PageToolsOverlay) =>
                {
                    overlay.mount();
                });
            }
        });

        previouslyRendered.map( (pageIndex) =>
        {
            if (newRenderedMap[pageIndex])
            {
                this._invokeOnOverlays(pageIndex, (overlay: PageToolsOverlay) =>
                {
                    overlay.refresh();
                });
            }
            else
            {
                delete this._renderedPageMap[pageIndex];
                this._invokeOnOverlays(pageIndex, (overlay: PageToolsOverlay) =>
                {
                    overlay.unmount();
                });
            }
        });

        this._renderedPages = renderedPages;
    }

    _invokeOnOverlays (pageIndex: number, func)
    {
        const overlays = this._pages[pageIndex];
        if (overlays)
        {
            overlays.map((o) => func(o));
        }
    }
}
