import './utils/vanilla.kinetic';
import './utils/dragscroll';
import { elt } from "./utils/elt";
import { DivaParentElementNotFoundException, NotAnIIIFManifestException, ObjectDataNotSuppliedException } from "./exceptions";
import globalDiva from "./diva-global";
import ViewerCore from "./viewer-core";
import ImageManifest from "./image-manifest";
import Toolbar from "./toolbar";
import HashParams from "./utils/hash-params";
class Diva {
    constructor(element, options) {
        if (!(element instanceof HTMLElement)) {
            this.element = document.getElementById(element);
            if (this.element === null) {
                throw new DivaParentElementNotFoundException();
            }
        }
        if (!options.objectData) {
            throw new ObjectDataNotSuppliedException('You must supply either a URL or a literal object to the `objectData` key.');
        }
        this.options = Object.assign({
            adaptivePadding: 0.05,
            arrowScrollAmount: 40,
            blockMobileMove: false,
            objectData: '',
            enableAutoTitle: true,
            enableFilename: true,
            enableFullscreen: true,
            enableGotoPage: true,
            enableGotoSuggestions: true,
            enableGridIcon: true,
            enableGridControls: 'buttons',
            enableImageTitles: true,
            enableIndexAsLabel: false,
            enableKeyScroll: true,
            enableLinkIcon: true,
            enableNonPagedVisibilityIcon: true,
            enableSpaceScroll: false,
            enableToolbar: true,
            enableZoomControls: 'buttons',
            fillParentHeight: true,
            fixedPadding: 10,
            fixedHeightGrid: true,
            goDirectlyTo: 0,
            hashParamSuffix: null,
            imageCrossOrigin: 'anonymous',
            inFullscreen: false,
            inBookLayout: false,
            inGrid: false,
            maxPagesPerRow: 8,
            maxZoomLevel: -1,
            minPagesPerRow: 2,
            minZoomLevel: 0,
            onGotoSubmit: null,
            pageAliases: {},
            pageAliasFunction: function () { return false; },
            pageLoadTimeout: 200,
            pagesPerRow: 5,
            requestHeaders: { "Accept": "application/json" },
            showNonPagedPages: false,
            throbberTimeout: 100,
            tileHeight: 256,
            tileWidth: 256,
            toolbarParentObject: null,
            verticallyOriented: true,
            viewportMargin: 200,
            zoomLevel: 2
        }, options);
        const wrapperElement = elt('div', {
            class: `diva-wrapper${this.options.fillParentHeight ? " diva-wrapper-flexbox" : ""}`
        });
        this.element.appendChild(wrapperElement);
        this.options.toolbarParentObject = this.options.toolbarParentObject || wrapperElement;
        const viewerCore = new ViewerCore(wrapperElement, this.options, this);
        this.viewerState = viewerCore.getInternalState();
        this.settings = viewerCore.getSettings();
        this.toolbar = this.settings.enableToolbar ? new Toolbar(this) : null;
        wrapperElement.id = this.settings.ID + 'wrapper';
        this.divaState = {
            viewerCore: viewerCore,
            toolbar: this.toolbar
        };
        let handle = globalDiva.Events.subscribe('ObjectDidLoad', () => {
            if (this.toolbar !== null) {
                this.toolbar.render();
            }
            globalDiva.Events.unsubscribe(handle);
        });
        this.hashState = this._getHashParamState();
        this._loadOrFetchObjectData();
    }
    _loadOrFetchObjectData() {
        if (typeof this.settings.objectData === 'object') {
            setTimeout(() => {
                this._loadObjectData(this.settings.objectData, this.hashState);
            }, 0);
        }
        else {
            const pendingManifestRequest = fetch(this.settings.objectData, {
                headers: this.settings.requestHeaders
            }).then((response) => {
                if (!response.ok) {
                    globalDiva.Events.publish('ManifestFetchError', [response], this);
                    this._ajaxError(response);
                    let error = new Error(response.statusText);
                    error.response = response;
                    throw error;
                }
                return response.json();
            }).then((data) => {
                this._loadObjectData(data, this.hashState);
            });
            this.divaState.viewerCore.setPendingManifestRequest(pendingManifestRequest);
        }
    }
    _showError(message) {
        this.divaState.viewerCore.showError(message);
    }
    _ajaxError(response) {
        const errorMessage = ['Invalid objectData setting. Error code: ' + response.status + ' ' + response.statusText];
        const dataHasAbsolutePath = this.settings.objectData.lastIndexOf('http', 0) === 0;
        if (dataHasAbsolutePath) {
            const jsonHost = this.settings.objectData.replace(/https?:\/\//i, "").split(/[/?#]/)[0];
            if (window.location.hostname !== jsonHost) {
                errorMessage.push(elt('p', 'Attempted to access cross-origin data without CORS.'), elt('p', 'You may need to update your server configuration to support CORS. For help, see the ', elt('a', {
                    href: 'https://github.com/DDMAL/diva.js/wiki/Installation#a-note-about-cross-site-requests',
                    target: '_blank'
                }, 'cross-site request documentation.')));
            }
        }
        this._showError(errorMessage);
    }
    _loadObjectData(responseData, hashState) {
        let manifest;
        if (!responseData.hasOwnProperty('@context') && (responseData['@context'].indexOf('iiif') === -1 || responseData['@context'].indexOf('shared-canvas') === -1)) {
            throw new NotAnIIIFManifestException('This does not appear to be a IIIF Manifest.');
        }
        globalDiva.Events.publish('ManifestDidLoad', [responseData], this);
        manifest = ImageManifest.fromIIIF(responseData);
        const loadOptions = hashState ? this._getLoadOptionsForState(hashState, manifest) : {};
        this.divaState.viewerCore.setManifest(manifest, loadOptions);
    }
    _getHashParamState() {
        const state = {};
        ['f', 'v', 'z', 'n', 'i', 'p', 'y', 'x'].forEach((param) => {
            const value = HashParams.get(param + this.settings.hashParamSuffix);
            if (value !== false) {
                state[param] = value;
            }
        });
        if (state.f === 'true')
            state.f = true;
        else if (state.f === 'false')
            state.f = false;
        ['z', 'n', 'p', 'x', 'y'].forEach((param) => {
            if (param in state) {
                state[param] = parseInt(state[param], 10);
            }
        });
        return state;
    }
    _getLoadOptionsForState(state, manifest) {
        manifest = manifest || this.settings.manifest;
        const options = ('v' in state) ? this._getViewState(state.v) : {};
        if ('f' in state) {
            options.inFullscreen = state.f;
        }
        if ('z' in state) {
            options.zoomLevel = state.z;
        }
        if ('n' in state) {
            options.pagesPerRow = state.n;
        }
        let pageIndex = this._getPageIndexForManifest(manifest, state.i);
        if (!(pageIndex >= 0 && pageIndex < manifest.pages.length)) {
            pageIndex = state.p - 1;
            if (!(pageIndex >= 0 && pageIndex < manifest.pages.length))
                pageIndex = null;
        }
        if (pageIndex !== null) {
            const horizontalOffset = parseInt(state.x, 10);
            const verticalOffset = parseInt(state.y, 10);
            options.goDirectlyTo = pageIndex;
            options.horizontalOffset = horizontalOffset;
            options.verticalOffset = verticalOffset;
        }
        return options;
    }
    _getViewState(view) {
        switch (view) {
            case 'd':
                return {
                    inGrid: false,
                    inBookLayout: false
                };
            case 'b':
                return {
                    inGrid: false,
                    inBookLayout: true
                };
            case 'g':
                return {
                    inGrid: true,
                    inBookLayout: false
                };
            default:
                return {};
        }
    }
    _getPageIndexForManifest(manifest, filename) {
        const np = manifest.pages.length;
        for (let i = 0; i < np; i++) {
            if (manifest.pages[i].f === filename) {
                return i;
            }
        }
        return -1;
    }
    _getState() {
        let view;
        if (this.settings.inGrid) {
            view = 'g';
        }
        else if (this.settings.inBookLayout) {
            view = 'b';
        }
        else {
            view = 'd';
        }
        const layout = this.divaState.viewerCore.getCurrentLayout();
        const pageOffset = layout.getPageToViewportCenterOffset(this.settings.activePageIndex, this.viewerState.viewport);
        return {
            'f': this.settings.inFullscreen,
            'v': view,
            'z': this.settings.zoomLevel,
            'n': this.settings.pagesPerRow,
            'i': this.settings.enableFilename ? this.settings.manifest.pages[this.settings.activePageIndex].f : false,
            'p': this.settings.enableFilename ? false : this.settings.activePageIndex + 1,
            'y': pageOffset ? pageOffset.y : false,
            'x': pageOffset ? pageOffset.x : false
        };
    }
    _getURLHash() {
        const hashParams = this._getState();
        const hashStringBuilder = [];
        for (const param in hashParams) {
            if (hashParams[param] !== false) {
                hashStringBuilder.push(param + this.settings.hashParamSuffix + '=' + encodeURIComponent(hashParams[param]));
            }
        }
        return hashStringBuilder.join('&');
    }
    _getPageIndex(filename) {
        return this._getPageIndexForManifest(this.settings.manifest, filename);
    }
    _checkLoaded() {
        if (!this.viewerState.loaded) {
            console.warn("The viewer is not completely initialized. This is likely because it is still downloading data. To fix this, only call this function if the isReady() method returns true.");
            return false;
        }
        return true;
    }
    _toggleFullscreen() {
        this._reloadViewer({
            inFullscreen: !this.settings.inFullscreen
        });
        let t;
        let hover = false;
        let tools = document.getElementById(this.settings.selector + 'tools');
        const TIMEOUT = 2000;
        if (this.settings.inFullscreen) {
            tools.classList.add("diva-fullscreen-tools");
            document.addEventListener('mousemove', toggleOpacity.bind(this));
            document.getElementsByClassName('diva-viewport')[0].addEventListener('scroll', toggleOpacity.bind(this));
            tools.addEventListener('mouseenter', function () {
                hover = true;
            });
            tools.addEventListener('mouseleave', function () {
                hover = false;
            });
        }
        else {
            tools.classList.remove("diva-fullscreen-tools");
        }
        function toggleOpacity() {
            tools.style.opacity = 1;
            clearTimeout(t);
            if (!hover && this.settings.inFullscreen) {
                t = setTimeout(function () {
                    tools.style.opacity = 0;
                }, TIMEOUT);
            }
        }
    }
    _togglePageLayoutOrientation() {
        const verticallyOriented = !this.settings.verticallyOriented;
        this._reloadViewer({
            inGrid: false,
            verticallyOriented: verticallyOriented,
            goDirectlyTo: this.settings.activePageIndex,
            verticalOffset: this.divaState.viewerCore.getYOffset(),
            horizontalOffset: this.divaState.viewerCore.getXOffset()
        });
        return verticallyOriented;
    }
    _changeView(destinationView) {
        switch (destinationView) {
            case 'document':
                return this._reloadViewer({
                    inGrid: false,
                    inBookLayout: false
                });
            case 'book':
                return this._reloadViewer({
                    inGrid: false,
                    inBookLayout: true
                });
            case 'grid':
                return this._reloadViewer({
                    inGrid: true
                });
            default:
                return false;
        }
    }
    _gotoPageByIndex(pageIndex, xAnchor, yAnchor) {
        let pidx = parseInt(pageIndex, 10);
        if (this._isPageIndexValid(pidx)) {
            const xOffset = this.divaState.viewerCore.getXOffset(pidx, xAnchor);
            const yOffset = this.divaState.viewerCore.getYOffset(pidx, yAnchor);
            this.viewerState.renderer.goto(pidx, yOffset, xOffset);
            return true;
        }
        return false;
    }
    _isPageIndexValid(pageIndex) {
        return this.settings.manifest.isPageValid(pageIndex, this.settings.showNonPagedPages);
    }
    _getPageIndexForPageXYValues(pageX, pageY) {
        const outerOffset = this.viewerState.outerElement.getBoundingClientRect();
        const outerTop = outerOffset.top;
        const outerLeft = outerOffset.left;
        const outerBottom = outerOffset.bottom;
        const outerRight = outerOffset.right;
        if (pageX < outerLeft || pageX > outerRight)
            return -1;
        if (pageY < outerTop || pageY > outerBottom)
            return -1;
        const pages = document.getElementsByClassName('diva-page');
        let curPageIdx = pages.length;
        while (curPageIdx--) {
            const curPage = pages[curPageIdx];
            const curOffset = curPage.getBoundingClientRect();
            if (pageX < curOffset.left || pageX > curOffset.right)
                continue;
            if (pageY < curOffset.top || pageY > curOffset.bottom)
                continue;
            return curPage.getAttribute('data-index');
        }
        return -1;
    }
    _reloadViewer(newOptions) {
        return this.divaState.viewerCore.reload(newOptions);
    }
    _getCurrentURL() {
        return location.protocol + '//' + location.host + location.pathname + location.search + '#' + this._getURLHash();
    }
    activate() {
        this.viewerState.isActiveDiva = true;
    }
    changeObject(objectData) {
        this.viewerState.loaded = false;
        this.divaState.viewerCore.clear();
        if (this.viewerState.renderer) {
            this.viewerState.renderer.destroy();
        }
        this.viewerState.options.objectData = objectData;
        this._loadOrFetchObjectData();
    }
    changeView(destinationView) {
        this._changeView(destinationView);
    }
    deactivate() {
        this.viewerState.isActiveDiva = false;
    }
    destroy() {
        this.divaState.viewerCore.destroy();
    }
    disableScrollable() {
        this.divaState.viewerCore.disableScrollable();
    }
    enableScrollable() {
        this.divaState.viewerCore.enableScrollable();
    }
    disableDragScrollable() {
        this.divaState.viewerCore.disableDragScrollable();
    }
    enableDragScrollable() {
        this.divaState.viewerCore.enableDragScrollable();
    }
    enterFullscreenMode() {
        if (!this.settings.inFullscreen) {
            this._toggleFullscreen();
            return true;
        }
        return false;
    }
    enterGridView() {
        if (!this.settings.inGrid) {
            this._changeView('grid');
            return true;
        }
        return false;
    }
    getAllPageURIs() {
        return this.settings.manifest.pages.map((pg) => {
            return pg.f;
        });
    }
    getCurrentCanvas() {
        return this.settings.manifest.pages[this.settings.activePageIndex].canvas;
    }
    getCurrentCanvasLabel() {
        return this.settings.manifest.pages[this.settings.activePageIndex].l;
    }
    getCurrentPageDimensionsAtCurrentZoomLevel() {
        return this.getPageDimensionsAtCurrentZoomLevel(this.settings.activePageIndex);
    }
    getCurrentPageFilename() {
        console.warn('This method will be deprecated in the next version of Diva. Please use getCurrentPageURI instead.');
        return this.settings.manifest.pages[this.settings.activePageIndex].f;
    }
    getCurrentPageIndices() {
        return this.settings.currentPageIndices;
    }
    getActivePageIndex() {
        return this.settings.activePageIndex;
    }
    getCurrentPageOffset() {
        return this.getPageOffset(this.settings.activePageIndex);
    }
    getCurrentPageURI() {
        return this.settings.manifest.pages[this.settings.activePageIndex].f;
    }
    getCurrentURL() {
        return this._getCurrentURL();
    }
    getFilenames() {
        console.warn('This will be removed in the next version of Diva. Use getAllPageURIs instead.');
        return this.settings.manifest.pages.map((pg) => {
            return pg.f;
        });
    }
    getGridPagesPerRow() {
        return this.settings.pagesPerRow;
    }
    getInstanceId() {
        return this.settings.ID;
    }
    getInstanceSelector() {
        return this.divaState.viewerCore.selector;
    }
    getItemTitle() {
        return this.settings.manifest.itemTitle;
    }
    getMaxZoomLevel() {
        return this.settings.maxZoomLevel;
    }
    getMaxZoomLevelForPage(pageIdx) {
        if (!this._checkLoaded())
            return false;
        return this.settings.manifest.pages[pageIdx].m;
    }
    getMinZoomLevel() {
        return this.settings.minZoomLevel;
    }
    getNumberOfPages() {
        if (!this._checkLoaded())
            return false;
        return this.settings.numPages;
    }
    getOtherImages(pageIndex) {
        return this.settings.manifest.pages[pageIndex].otherImages;
    }
    getPageDimensions(pageIndex) {
        if (!this._checkLoaded())
            return null;
        return this.divaState.viewerCore.getCurrentLayout().getPageDimensions(pageIndex);
    }
    getPageDimensionsAtCurrentZoomLevel(pageIndex) {
        let pidx = parseInt(pageIndex, 10);
        if (!this._isPageIndexValid(pidx))
            throw new Error('Invalid Page Index');
        return this.divaState.viewerCore.getCurrentLayout().getPageDimensions(pidx);
    }
    getPageDimensionsAtZoomLevel(pageIdx, zoomLevel) {
        if (!this._checkLoaded())
            return false;
        if (zoomLevel > this.settings.maxZoomLevel)
            zoomLevel = this.settings.maxZoomLevel;
        const pg = this.settings.manifest.pages[parseInt(pageIdx, 10)];
        const pgAtZoom = pg.d[parseInt(zoomLevel, 10)];
        return {
            width: pgAtZoom.w,
            height: pgAtZoom.h
        };
    }
    getPageImageURL(pageIndex, size) {
        return this.settings.manifest.getPageImageURL(pageIndex, size);
    }
    getPageIndexForPageXYValues(pageX, pageY) {
        return this._getPageIndexForPageXYValues(pageX, pageY);
    }
    getPageOffset(pageIndex, options) {
        const region = this.divaState.viewerCore.getPageRegion(pageIndex, options);
        return {
            top: region.top,
            left: region.left
        };
    }
    getSettings() {
        return this.settings;
    }
    getState() {
        return this._getState();
    }
    getZoomLevel() {
        return this.settings.zoomLevel;
    }
    gotoPageByIndex(pageIndex, xAnchor, yAnchor) {
        return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
    }
    gotoPageByLabel(label, xAnchor, yAnchor) {
        const pages = this.settings.manifest.pages;
        let llc = label.toLowerCase();
        for (let i = 0, len = pages.length; i < len; i++) {
            if (pages[i].l.toLowerCase().indexOf(llc) > -1)
                return this._gotoPageByIndex(i, xAnchor, yAnchor);
        }
        const pageIndex = parseInt(label, 10) - 1;
        return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
    }
    gotoPageByName(filename, xAnchor, yAnchor) {
        console.warn('This method will be removed in the next version of Diva.js. Use gotoPageByURI instead.');
        const pageIndex = this._getPageIndex(filename);
        return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
    }
    gotoPageByURI(uri, xAnchor, yAnchor) {
        const pageIndex = this._getPageIndex(uri);
        return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
    }
    hasOtherImages(pageIndex) {
        return this.settings.manifest.pages[pageIndex].otherImages === true;
    }
    hideNonPagedPages() {
        this._reloadViewer({ showNonPagedPages: false });
    }
    isInFullscreen() {
        return this.settings.inFullscreen;
    }
    isPageIndexValid(pageIndex) {
        return this._isPageIndexValid(pageIndex);
    }
    isPageInViewport(pageIndex) {
        return this.viewerState.renderer.isPageVisible(pageIndex);
    }
    isReady() {
        return this.viewerState.loaded;
    }
    isRegionInViewport(pageIndex, leftOffset, topOffset, width, height) {
        const layout = this.divaState.viewerCore.getCurrentLayout();
        if (!layout)
            return false;
        const offset = layout.getPageOffset(pageIndex);
        const top = offset.top + topOffset;
        const left = offset.left + leftOffset;
        return this.viewerState.viewport.intersectsRegion({
            top: top,
            bottom: top + height,
            left: left,
            right: left + width
        });
    }
    isVerticallyOriented() {
        return this.settings.verticallyOriented;
    }
    leaveFullscreenMode() {
        if (this.settings.inFullscreen) {
            this._toggleFullscreen();
            return true;
        }
        return false;
    }
    leaveGridView() {
        if (this.settings.inGrid) {
            this._reloadViewer({ inGrid: false });
            return true;
        }
        return false;
    }
    setGridPagesPerRow(pagesPerRow) {
        if (!this.divaState.viewerCore.isValidOption('pagesPerRow', pagesPerRow))
            return false;
        return this._reloadViewer({
            inGrid: true,
            pagesPerRow: pagesPerRow
        });
    }
    setState(state) {
        this._reloadViewer(this._getLoadOptionsForState(state));
    }
    setZoomLevel(zoomLevel) {
        if (this.settings.inGrid) {
            this._reloadViewer({
                inGrid: false
            });
        }
        return this.divaState.viewerCore.zoom(zoomLevel);
    }
    showNonPagedPages() {
        this._reloadViewer({ showNonPagedPages: true });
    }
    toggleFullscreenMode() {
        this._toggleFullscreen();
    }
    toggleNonPagedPagesVisibility() {
        this._reloadViewer({
            showNonPagedPages: !this.settings.showNonPagedPages
        });
    }
    toggleOrientation() {
        return this._togglePageLayoutOrientation();
    }
    translateFromMaxZoomLevel(position) {
        const zoomDifference = this.settings.maxZoomLevel - this.settings.zoomLevel;
        return position / Math.pow(2, zoomDifference);
    }
    translateToMaxZoomLevel(position) {
        const zoomDifference = this.settings.maxZoomLevel - this.settings.zoomLevel;
        if (zoomDifference === 0)
            return position;
        return position * Math.pow(2, zoomDifference);
    }
    zoomIn() {
        return this.setZoomLevel(this.settings.zoomLevel + 1);
    }
    zoomOut() {
        return this.setZoomLevel(this.settings.zoomLevel - 1);
    }
}
Diva.Events = diva.Events;
export default Diva;
if (typeof window !== 'undefined') {
    (function (global) {
        global.Diva = global.Diva || Diva;
    })(window);
}
//# sourceMappingURL=diva.js.map