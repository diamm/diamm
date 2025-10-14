(() => { // webpackBootstrap
var __webpack_modules__ = ({
"./source/css/diva.scss": (function (module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
// extracted by css-extract-rspack-plugin

    if(true) {
      (function() {
        var localsJsonString = undefined;
        // 1745419584194
        var cssReload = (__webpack_require__("./node_modules/@rspack/core/dist/cssExtractHmr.js")/* .cssReload */.cssReload)(module.id, {});
        // only invalidate when locals change
        if (
          module.hot.data &&
          module.hot.data.value &&
          module.hot.data.value !== localsJsonString
        ) {
          module.hot.invalidate();
        } else {
          module.hot.accept();
        }
        module.hot.dispose(function(data) {
          data.value = localsJsonString;
          cssReload();
        });
      })();
    }
  

}),
"./source/js/composite-image.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (CompositeImage)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _tile_coverage_map__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/tile-coverage-map.ts");


class CompositeImage {
    clear() {
        const loadedByLevel = this._loadedByLevel = {};
        this._levels.forEach((level)=>{
            loadedByLevel[level.zoomLevel] = new _tile_coverage_map__WEBPACK_IMPORTED_MODULE_0__["default"](level.rows, level.cols);
        });
    }
    getTiles(baseZoomLevel) {
        const toRenderByLevel = [];
        const highestZoomLevel = this._levels[0].zoomLevel;
        const covered = new _tile_coverage_map__WEBPACK_IMPORTED_MODULE_0__["default"](this._levels[0].rows, this._levels[0].cols);
        let bestLevelIndex;
        // Default to the lowest zoom level
        if (baseZoomLevel === null) {
            bestLevelIndex = 0;
        } else {
            const ceilLevel = Math.ceil(baseZoomLevel);
            bestLevelIndex = findIndex(this._levels, (level)=>level.zoomLevel <= ceilLevel);
        // bestLevelIndex = this._levels.findIndex((level) => level.zoomLevel <= ceilLevel);
        }
        // The best level, followed by higher-res levels in ascending order of resolution,
        // followed by lower-res levels in descending order of resolution
        const levelsByPreference = this._levels.slice(0, bestLevelIndex + 1).reverse().concat(this._levels.slice(bestLevelIndex + 1));
        levelsByPreference.forEach((level)=>{
            const loaded = this._loadedByLevel[level.zoomLevel];
            let additionalTiles = level.tiles.filter((tile)=>loaded.isLoaded(tile.row, tile.col));
            // Filter out entirely covered tiles
            // FIXME: Is it better to draw all of a partially covered tile,
            // with some of it ultimately covered, or to pick out the region
            // which needs to be drawn?
            // See https://github.com/DDMAL/diva.js/issues/358
            const scaleRatio = Math.pow(2, highestZoomLevel - level.zoomLevel);
            additionalTiles = additionalTiles.filter((tile)=>{
                let isNeeded = false;
                const highResRow = tile.row * scaleRatio;
                const highResCol = tile.col * scaleRatio;
                for(let i = 0; i < scaleRatio; i++){
                    for(let j = 0; j < scaleRatio; j++){
                        if (!covered.isLoaded(highResRow + i, highResCol + j)) {
                            isNeeded = true;
                            covered.set(highResRow + i, highResCol + j, true);
                        }
                    }
                }
                return isNeeded;
            });
            toRenderByLevel.push(additionalTiles);
        });
        // Less-preferred tiles should come first
        toRenderByLevel.reverse();
        const tiles = [];
        toRenderByLevel.forEach((byLevel)=>{
            tiles.push.apply(tiles, byLevel);
        });
        return tiles;
    }
    /**
     * Update the composite image to take into account all the URLs
     * loaded in an image cache.
     *
     * @param cache {ImageCache}
     */ updateFromCache(cache) {
        this.clear();
        this._levels.forEach((level)=>{
            const loaded = this._loadedByLevel[level.zoomLevel];
            level.tiles.forEach((tile)=>{
                if (cache.has(tile.url)) {
                    loaded.set(tile.row, tile.col, true);
                }
            });
        }, this);
    }
    updateWithLoadedUrls(urls) {
        urls.forEach((url)=>{
            const entry = this._urlsToTiles[url];
            this._loadedByLevel[entry.zoomLevel].set(entry.row, entry.col, true);
        });
    }
    constructor(levels){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_levels", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_urlsToTiles", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_loadedByLevel", void 0);
        this._levels = levels; // Assume levels sorted high-res first
        const urlsToTiles = this._urlsToTiles = {};
        levels.forEach((level)=>{
            level.tiles.forEach((tile)=>{
                urlsToTiles[tile.url] = {
                    zoomLevel: level.zoomLevel,
                    row: tile.row,
                    col: tile.col
                };
            });
        });
        this.clear();
    }
}
/**
 * @class CompositeImage
 * @private
 *
 * Utility class to composite tiles into a complete image
 * and track the rendered state of an image as new tiles
 * load.
 */ 
// function fill (count, value)
// {
//     const arr = new Array(count);
//
//     for (let i=0; i < count; i++)
//         arr[i] = value;
//
//     return arr;
// }
function findIndex(array, predicate) {
    const length = array.length;
    for(let i = 0; i < length; i++){
        if (predicate(array[i], i)) {
            return i;
        }
    }
    return -1;
}


}),
"./source/js/diva-global.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__WEBPACK_DEFAULT_EXPORT__)
});
/* ESM import */var _utils_events__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/events.ts");

const diva = {
    Events: _utils_events__WEBPACK_IMPORTED_MODULE_0__.Events
};
/* ESM default export */ const __WEBPACK_DEFAULT_EXPORT__ = (diva);


}),
"./source/js/diva.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__WEBPACK_DEFAULT_EXPORT__)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _utils_vanilla_kinetic__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/vanilla.kinetic.ts");
/* ESM import */var _utils_vanilla_kinetic__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_utils_vanilla_kinetic__WEBPACK_IMPORTED_MODULE_0__);
/* ESM import */var _utils_dragscroll__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./source/js/utils/dragscroll.js");
/* ESM import */var _utils_dragscroll__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_utils_dragscroll__WEBPACK_IMPORTED_MODULE_1__);
/* ESM import */var _utils_elt__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__("./source/js/utils/elt.ts");
/* ESM import */var _exceptions__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__("./source/js/exceptions.ts");
/* ESM import */var _diva_global__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__("./source/js/diva-global.ts");
/* ESM import */var _viewer_core__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__("./source/js/viewer-core.ts");
/* ESM import */var _image_manifest__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__("./source/js/image-manifest.ts");
/* ESM import */var _toolbar__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__("./source/js/toolbar.ts");
/* ESM import */var _utils_hash_params__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__("./source/js/utils/hash-params.ts");










/**
 * The top-level class for Diva objects. This is instantiated by passing in an HTML element
 * ID or HTML Element node and an object containing a list of options, of which the 'objectData'
 * option is required and which must point to a IIIF Presentation API Manifest:
 *
 * var diva = new Diva('element-id', {
 *     objectData: "http://example.com/iiif-manifest.json"
 * });
 *
 * This class also serves as the entry point for the Events system, in which applications can subscribe
 * to notifications sent from Diva instances:
 *
 * Diva.Events.subscribe('VisiblePageDidChange', function () { console.log("Visible Page Changed"); });
 *
 *
 *
 **/ class Diva {
    /**
     * @private
     **/ _loadOrFetchObjectData() {
        if (typeof this.settings.objectData === 'object') {
            // Defer execution until initialization has completed
            setTimeout(()=>{
                this._loadObjectData(this.settings.objectData, this.hashState);
            }, 0);
        } else {
            const pendingManifestRequest = fetch(this.settings.objectData, {
                headers: this.settings.requestHeaders
            }).then((response)=>{
                if (!response.ok) {
                    // trigger manifest load error event
                    _diva_global__WEBPACK_IMPORTED_MODULE_4__["default"].Events.publish('ManifestFetchError', [
                        response
                    ], this);
                    this._ajaxError(response);
                    let error = new Error(response.statusText);
                    error.response = response;
                    throw error;
                }
                return response.json();
            }).then((data)=>{
                this._loadObjectData(data, this.hashState);
            });
            // Store the pending request so that it can be cancelled in the event that Diva needs to be destroyed
            this.divaState.viewerCore.setPendingManifestRequest(pendingManifestRequest);
        }
    }
    /**
     * @private
     **/ _showError(message) {
        this.divaState.viewerCore.showError(message);
    }
    /**
     * @private
     * */ _ajaxError(response) {
        // Show a basic error message within the document viewer pane
        const errorMessage = [
            'Invalid objectData setting. Error code: ' + response.status + ' ' + response.statusText
        ];
        // Detect and handle CORS errors
        const dataHasAbsolutePath = this.settings.objectData.lastIndexOf('http', 0) === 0;
        if (dataHasAbsolutePath) {
            const jsonHost = this.settings.objectData.replace(/https?:\/\//i, "").split(/[/?#]/)[0];
            if (window.location.hostname !== jsonHost) {
                errorMessage.push((0,_utils_elt__WEBPACK_IMPORTED_MODULE_2__.elt)('p', 'Attempted to access cross-origin data without CORS.'), (0,_utils_elt__WEBPACK_IMPORTED_MODULE_2__.elt)('p', 'You may need to update your server configuration to support CORS. For help, see the ', (0,_utils_elt__WEBPACK_IMPORTED_MODULE_2__.elt)('a', {
                    href: 'https://github.com/DDMAL/diva.js/wiki/Installation#a-note-about-cross-site-requests',
                    target: '_blank'
                }, 'cross-site request documentation.')));
            }
        }
        this._showError(errorMessage);
    }
    /**
     * @private
     **/ _loadObjectData(responseData, hashState) {
        let manifest;
        // TODO improve IIIF detection method
        if (!responseData.hasOwnProperty('@context') && (responseData['@context'].indexOf('iiif') === -1 || responseData['@context'].indexOf('shared-canvas') === -1)) {
            throw new _exceptions__WEBPACK_IMPORTED_MODULE_3__.NotAnIIIFManifestException('This does not appear to be a IIIF Manifest.');
        }
        // trigger ManifestDidLoad event
        _diva_global__WEBPACK_IMPORTED_MODULE_4__["default"].Events.publish('ManifestDidLoad', [
            responseData
        ], this);
        manifest = _image_manifest__WEBPACK_IMPORTED_MODULE_6__["default"].fromIIIF(responseData);
        const loadOptions = hashState ? this._getLoadOptionsForState(hashState, manifest) : {};
        this.divaState.viewerCore.setManifest(manifest, loadOptions);
    }
    /**
     * Parse the hash parameters into the format used by getState and setState
     *
     * @private
     **/ _getHashParamState() {
        const state = {};
        [
            'f',
            'v',
            'z',
            'n',
            'i',
            'p',
            'y',
            'x'
        ].forEach((param)=>{
            const value = _utils_hash_params__WEBPACK_IMPORTED_MODULE_8__["default"].get(param + this.settings.hashParamSuffix);
            // `false` is returned if the value is missing
            if (value !== false) {
                state[param] = value;
            }
        });
        // Do some awkward special-casing, since this format is kind of weird.
        // For inFullscreen (f), true and false strings should be interpreted
        // as booleans.
        if (state.f === 'true') {
            state.f = true;
        } else if (state.f === 'false') {
            state.f = false;
        }
        // Convert numerical values to integers, if provided
        [
            'z',
            'n',
            'p',
            'x',
            'y'
        ].forEach((param)=>{
            if (param in state) {
                state[param] = parseInt(state[param], 10);
            }
        });
        return state;
    }
    /**
     * @private
     **/ _getLoadOptionsForState(state, manifest) {
        manifest = manifest || this.settings.manifest;
        const options = 'v' in state ? this._getViewState(state.v) : {};
        if ('f' in state) {
            options.inFullscreen = state.f;
        }
        if ('z' in state) {
            options.zoomLevel = state.z;
        }
        if ('n' in state) {
            options.pagesPerRow = state.n;
        }
        // Only change specify the page if state.i or state.p is valid
        let pageIndex = this._getPageIndexForManifest(manifest, state.i);
        if (!(pageIndex >= 0 && pageIndex < manifest.pages.length)) {
            pageIndex = state.p - 1;
            // Possibly NaN
            if (!(pageIndex >= 0 && pageIndex < manifest.pages.length)) {
                pageIndex = -1;
            }
        }
        if (pageIndex >= 0) {
            const horizontalOffset = parseInt(state.x, 10);
            const verticalOffset = parseInt(state.y, 10);
            options.goDirectlyTo = pageIndex;
            options.horizontalOffset = horizontalOffset;
            options.verticalOffset = verticalOffset;
        }
        return options;
    }
    /**
     * @private
     * */ _getViewState(view) {
        switch(view){
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
    /**
     * @private
     * */ _getPageIndexForManifest(manifest, filename) {
        const np = manifest.pages.length;
        for(let i = 0; i < np; i++){
            if (manifest.pages[i].f === filename) {
                return i;
            }
        }
        return -1;
    }
    /**
     * @private
     * */ _getState() {
        let view;
        if (this.settings.inGrid) {
            view = 'g';
        } else if (this.settings.inBookLayout) {
            view = 'b';
        } else {
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
            'y': pageOffset ? pageOffset.y : 0,
            'x': pageOffset ? pageOffset.x : 0
        };
    }
    /**
     * @private
     **/ _getURLHash() {
        const hashParams = this._getState();
        const hashStringBuilder = [];
        for(const param in hashParams){
            if (hashParams[param] !== false) {
                hashStringBuilder.push(param + this.settings.hashParamSuffix + '=' + encodeURIComponent(hashParams[param]));
            }
        }
        return hashStringBuilder.join('&');
    }
    /**
     * Returns the page index associated with the given filename; must called after setting settings.manifest
     *
     * @private
     **/ _getPageIndex(filename) {
        return this._getPageIndexForManifest(this.settings.manifest, filename);
    }
    /**
     * @private
     * */ _checkLoaded() {
        if (!this.viewerState.loaded) {
            console.warn("The viewer is not completely initialized. This is likely because it is still downloading data. To fix this, only call this function if the isReady() method returns true.");
            return false;
        }
        return true;
    }
    /**
     * Called when the fullscreen icon is clicked
     *
     * @private
     **/ _toggleFullscreen() {
        this._reloadViewer({
            inFullscreen: !this.settings.inFullscreen
        });
        let hover = false;
        let tools = document.getElementById(this.settings.selector + 'tools');
        if (!tools) {
            return;
        }
        const TIMEOUT = 2000;
        if (this.settings.inFullscreen) {
            tools.classList.add("diva-fullscreen-tools");
            document.addEventListener('mousemove', toggleOpacity.bind(this));
            document.getElementsByClassName('diva-viewport')[0].addEventListener('scroll', toggleOpacity.bind(this));
            tools.addEventListener('mouseenter', function() {
                hover = true;
            });
            tools.addEventListener('mouseleave', function() {
                hover = false;
            });
        } else {
            tools.classList.remove("diva-fullscreen-tools");
        }
        let t;
        function toggleOpacity() {
            tools.style.opacity = "1";
            clearTimeout(t);
            if (!hover && this.settings.inFullscreen) {
                t = setTimeout(function() {
                    tools.style.opacity = "0";
                }, TIMEOUT);
            }
        }
    }
    /**
     * Toggles between orientations
     *
     * @private
     * */ _togglePageLayoutOrientation() {
        const verticallyOriented = !this.settings.verticallyOriented;
        //if in grid, switch out of grid
        this._reloadViewer({
            inGrid: false,
            verticallyOriented: verticallyOriented,
            goDirectlyTo: this.settings.activePageIndex,
            verticalOffset: this.divaState.viewerCore.getYOffset(),
            horizontalOffset: this.divaState.viewerCore.getXOffset()
        });
        return verticallyOriented;
    }
    /**
     * Called when the change view icon is clicked
     *
     * @private
     **/ _changeView(destinationView) {
        switch(destinationView){
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
    /**
     * @private
     *
     * @param {Number} pageIndex - 0-based page index.
     * @param {Number} xAnchor - x coordinate to jump to on resulting page.
     * @param {Number} yAnchor - y coordinate to jump to on resulting page.
     * @returns {Boolean} - Whether the jump was successful.
     **/ _gotoPageByIndex(pageIndex, xAnchor, yAnchor) {
        if (this._isPageIndexValid(pageIndex)) {
            const xOffset = this.divaState.viewerCore.getXOffset(pageIndex, xAnchor);
            const yOffset = this.divaState.viewerCore.getYOffset(pageIndex, yAnchor);
            this.viewerState.renderer.goto(pageIndex, yOffset, xOffset);
            return true;
        }
        return false;
    }
    /**
     * Check if a page index is valid
     *
     * @private
     * @param {Number} pageIndex - Numeric (0-based) page index
     * @return {Boolean} whether the page index is valid or not.
     */ _isPageIndexValid(pageIndex) {
        return this.settings.manifest.isPageValid(pageIndex, this.settings.showNonPagedPages);
    }
    /**
     * Given a pageX and pageY value, returns either the page visible at that (x,y)
     * position or -1 if no page is.
     *
     * @private
     */ _getPageIndexForPageXYValues(pageX, pageY) {
        //get the four edges of the outer element
        const outerOffset = this.viewerState.outerElement.getBoundingClientRect();
        const outerTop = outerOffset.top;
        const outerLeft = outerOffset.left;
        const outerBottom = outerOffset.bottom;
        const outerRight = outerOffset.right;
        //if the clicked position was outside the diva-outer object, it was not on a visible portion of a page
        if (pageX < outerLeft || pageX > outerRight) {
            return -1;
        }
        if (pageY < outerTop || pageY > outerBottom) {
            return -1;
        }
        //navigate through all diva page objects
        const pages = document.getElementsByClassName('diva-page');
        let curPageIdx = pages.length;
        while(curPageIdx--){
            //get the offset for each page
            const curPage = pages[curPageIdx];
            const curOffset = curPage.getBoundingClientRect();
            //if this point is outside the horizontal boundaries of the page, continue
            if (pageX < curOffset.left || pageX > curOffset.right) {
                continue;
            }
            //same with vertical boundaries
            if (pageY < curOffset.top || pageY > curOffset.bottom) {
                continue;
            }
            //if we made it through the above two, we found the page we're looking for
            return parseInt(curPage.getAttribute('data-index'), 10);
        }
        //if we made it through that entire while loop, we didn't click on a page
        return -1;
    }
    /**
     * @private
     **/ _reloadViewer(newOptions) {
        return this.divaState.viewerCore.reload(newOptions);
    }
    /**
     * @private
     */ _getCurrentURL() {
        return location.protocol + '//' + location.host + location.pathname + location.search + '#' + this._getURLHash();
    }
    /**
     * ===============================================
     *                PUBLIC FUNCTIONS
     * ===============================================
     **/ /**
     *  Activate this instance of diva via the active Diva controller.
     *
     *  @public
     */ activate() {
        this.viewerState.isActiveDiva = true;
    }
    /**
     * Change the object (objectData) parameter currently being rendered by Diva.
     *
     * @public
     * @params {object} objectData - An IIIF Manifest object OR a URL to a IIIF manifest.
     */ changeObject(objectData) {
        this.viewerState.loaded = false;
        this.divaState.viewerCore.clear();
        if (this.viewerState.renderer) {
            this.viewerState.renderer.destroy();
        }
        this.viewerState.options.objectData = objectData;
        this._loadOrFetchObjectData();
    }
    /**
     * Change views. Takes 'document', 'book', or 'grid' to specify which view to switch into
     *
     * @public
     * @params {string} destinationView - the destination view to change to.
     */ changeView(destinationView) {
        return this._changeView(destinationView);
    }
    /**
     *  Deactivate this diva instance through the active Diva controller.
     *
     *  @public
     **/ deactivate() {
        this.viewerState.isActiveDiva = false;
    }
    /**
     * Destroys this instance, tells plugins to do the same
     *
     * @public
     **/ destroy() {
        this.divaState.viewerCore.destroy();
    }
    /**
     * Disables document dragging, scrolling (by keyboard if set), and zooming by double-clicking
     *
     * @public
     **/ disableScrollable() {
        this.divaState.viewerCore.disableScrollable();
    }
    /**
     * Re-enables document dragging, scrolling (by keyboard if set), and zooming by double-clicking
     *
     * @public
     **/ enableScrollable() {
        this.divaState.viewerCore.enableScrollable();
    }
    /**
     * Disables document drag scrolling
     *
     * @public
     */ disableDragScrollable() {
        this.divaState.viewerCore.disableDragScrollable();
    }
    /**
     * Enables document drag scrolling
     *
     * @public
     */ enableDragScrollable() {
        this.divaState.viewerCore.enableDragScrollable();
    }
    /**
     * Enter fullscreen mode if currently not in fullscreen mode. If currently in fullscreen
     * mode this will have no effect.
     *
     * This function will work even if enableFullscreen is set to false in the options.
     *
     * @public
     * @returns {boolean} - Whether the switch to fullscreen was successful or not.
     **/ enterFullscreenMode() {
        if (!this.settings.inFullscreen) {
            this._toggleFullscreen();
            return true;
        }
        return false;
    }
    /**
     * Enter grid view if currently not in grid view. If currently in grid view mode
     * this will have no effect.
     *
     * @public
     * @returns {boolean} - Whether the switch to grid view was successful or not.
     **/ enterGridView() {
        if (!this.settings.inGrid) {
            this._changeView('grid');
            return true;
        }
        return false;
    }
    /**
     * Returns an array of all page image URIs in the document.
     *
     * @public
     * @returns {Array} - An array of all the URIs in the document.
     * */ getAllPageURIs() {
        return this.settings.manifest.pages.map((pg)=>{
            return pg.f;
        });
    }
    /**
     * Get the canvas identifier for the currently visible page.
     *
     * @public
     * @returns {string} - The URI of the currently visible canvas.
     **/ getCurrentCanvas() {
        return this.settings.manifest.pages[this.settings.activePageIndex].canvas;
    }
    /**
     * Get the canvas label for the currently visible page.
     *
     * @public
     * @returns {string} - The label of the currently visible canvas.
     **/ getCurrentCanvasLabel() {
        return this.settings.manifest.pages[this.settings.activePageIndex].l;
    }
    /**
     * Returns the dimensions of the current page at the current zoom level. Also works in
     * grid view.
     *
     * @public
     * @returns {object} - An object containing the current page dimensions at the current zoom level.
     **/ getCurrentPageDimensionsAtCurrentZoomLevel() {
        return this.getPageDimensionsAtCurrentZoomLevel(this.settings.activePageIndex);
    }
    /**
     * Returns an array of page indices that are visible in the viewport.
     *
     * @public
     * @returns {array} - The 0-based indices array for the currently visible pages.
     **/ getCurrentPageIndices() {
        return this.settings.currentPageIndices;
    }
    /**
     * Returns the 0-based index for the current page.
     *
     * @public
     * @returns {number} - The 0-based index for the currently visible page.
     **/ getActivePageIndex() {
        return this.settings.activePageIndex;
    }
    /**
     * Shortcut to getPageOffset for current page.
     *
     * @public
     * @returns {object} - The offset between the upper left corner and the page.
     * */ getCurrentPageOffset() {
        return this.getPageOffset(this.settings.activePageIndex);
    }
    /**
     * Returns the current URI for the visible page.
     *
     * @public
     * @returns {string} - The URI for the current page image.
     **/ getCurrentPageURI() {
        return this.settings.manifest.pages[this.settings.activePageIndex].f;
    }
    /**
     * Return the current URL for the viewer, including the hash parameters reflecting
     * the current state of the viewer.
     *
     * @public
     * @returns {string} - The URL for the current view state.
     * */ getCurrentURL() {
        return this._getCurrentURL();
    }
    /**
     * Get the number of grid pages per row.
     *
     * @public
     * @returns {number} - The number of grid pages per row.
     **/ getGridPagesPerRow() {
        // TODO(wabain): Add test case
        return this.settings.pagesPerRow;
    }
    /**
     * Get the instance ID number.
     *
     * @public
     * @returns {number} - The instance ID.
     * */ //
    getInstanceId() {
        return this.settings.ID;
    }
    /**
     * Get the instance selector for this instance. This is the selector for the parent
     * div.
     *
     * @public
     * @returns {string} - The viewport selector.
     * */ getInstanceSelector() {
        return this.divaState.viewerCore.viewerState.selector;
    }
    /**
     * Returns the title of the document, based on the label in the IIIF manifest.
     *
     * @public
     * @returns {string} - The current title of the object from the label key in the IIIF Manifest.
     **/ getItemTitle() {
        return this.settings.manifest.itemTitle;
    }
    /**
     * Gets the maximum zoom level for the entire document.
     *
     * @public
     * @returns {number} - The maximum zoom level for the document
     * */ getMaxZoomLevel() {
        return this.settings.maxZoomLevel;
    }
    /**
     * Gets the max zoom level for a given page.
     *
     * @public
     * @param {number} pageIdx - The 0-based index number for the page.
     * @returns {number} - The maximum zoom level for that page.
     * */ getMaxZoomLevelForPage(pageIdx) {
        if (!this._checkLoaded()) {
            return null;
        }
        return this.settings.manifest.pages[pageIdx].m;
    }
    /**
     * Gets the minimum zoom level for the entire document.
     *
     * @public
     * @returns {number} - The minimum zoom level for the document
     * */ getMinZoomLevel() {
        return this.settings.minZoomLevel;
    }
    /**
     * Gets the number of pages in the document.
     *
     * @public
     * @returns {number} - The number of pages in the document.
     * */ getNumberOfPages() {
        if (!this._checkLoaded()) {
            return false;
        }
        return this.settings.numPages;
    }
    /**
     * If a canvas has multiple images defined, returns the non-primary image.
     *
     * @public
     * @params {number} pageIndex - The page index for which to return the other images.
     * @returns {object} An object containing the other images.
     **/ getOtherImages(pageIndex) {
        return this.settings.manifest.pages[pageIndex].otherImages;
    }
    /**
     * Get page dimensions in the current view and zoom level
     *
     * @public
     * @params {number} pageIndex - A valid 0-based page index
     * @returns {object} - An object containing the dimensions of the page
     * */ getPageDimensions(pageIndex) {
        if (!this._checkLoaded()) {
            return null;
        }
        return this.divaState.viewerCore.getCurrentLayout().getPageDimensions(pageIndex);
    }
    /**
     * Returns the dimensions of a given page at the current zoom level.
     * Also works in Grid view
     *
     * @public
     * @param {number} pageIndex - The 0-based page index
     * @returns {object} - An object containing the page dimensions at the current zoom level.
     * */ getPageDimensionsAtCurrentZoomLevel(pageIndex) {
        if (!this._isPageIndexValid(pageIndex)) {
            throw new Error('Invalid Page Index');
        }
        return this.divaState.viewerCore.getCurrentLayout().getPageDimensions(pageIndex);
    }
    /**
     * Get page dimensions at a given zoom level
     *
     * @public
     * @params {number} pageIdx - A valid 0-based page index
     * @params {number} zoomLevel - A candidate zoom level.
     * @returns {object} - An object containing the dimensions of the page at the given zoom level.
     **/ getPageDimensionsAtZoomLevel(pageIdx, zoomLevel) {
        if (!this._checkLoaded()) {
            return null;
        }
        if (zoomLevel > this.settings.maxZoomLevel) {
            zoomLevel = this.settings.maxZoomLevel;
        }
        const pg = this.settings.manifest.pages[pageIdx];
        const pgAtZoom = pg.d[zoomLevel];
        return {
            width: pgAtZoom.w,
            height: pgAtZoom.h
        };
    }
    /**
     * Returns a URL for the image of the page at the given index. The
     * optional size parameter supports setting the image width or height
     * (default is full-sized).
     *
     * @public
     * @params {number} pageIndex - 0-based page index
     * @params {?object} size - an object containing width and height information
     * @returns {string} - The IIIF URL for a given page at an optional size
     */ getPageImageURL(pageIndex, size) {
        return this.settings.manifest.getPageImageURL(pageIndex, size);
    }
    /**
     * Given a set of co-ordinates (e.g., from a mouse click), return the 0-based page index
     * for which it matches.
     *
     * @public
     * @params {number} pageX - The x co-ordinate
     * @params {number} pageY - The y co-ordinate
     * @returns {number} - The page index matching the co-ordinates.
     * */ getPageIndexForPageXYValues(pageX, pageY) {
        return this._getPageIndexForPageXYValues(pageX, pageY);
    }
    /**
     * Returns distance between the northwest corners of diva-inner and page index.
     *
     * @public
     * @params {number} pageIndex - The 0-based page index
     * @params {?options} options - A set of options to pass in.
     * @returns {object} - The offset between the upper left corner and the page.
     *
     * */ getPageOffset(pageIndex, options) {
        const region = this.divaState.viewerCore.getPageRegion(pageIndex, options);
        return {
            top: region.top,
            left: region.left
        };
    }
    /**
     * Get the instance settings.
     *
     * @public
     * @returns {object} - The current instance settings.
     * */ getSettings() {
        return this.settings;
    }
    /**
     * Get an object representing the complete state of the viewer.
     *
     * @public
     * @returns {object} - The current instance state.
     * */ getState() {
        return this._getState();
    }
    /**
     * Get the current zoom level.
     *
     * @public
     * @returns {number} - The current zoom level.
     * */ getZoomLevel() {
        return this.settings.zoomLevel;
    }
    /**
     *  Go to a particular page (with indexing starting at 0).
     *  The (xAnchor) side of the page will be anchored to the (xAnchor) side of the diva-outer element
     *
     *  @public
     *  @params {number} pageIndex - 0-based page index.
     *  @params {?string} xAnchor - may either be "left", "right", or default "center"
     *  @params {?string} yAnchor - may either be "top", "bottom", or default "center"; same process as xAnchor.
     *  @returns {boolean} - True if the page index is valid; false if it is not.
     * */ gotoPageByIndex(pageIndex, xAnchor, yAnchor) {
        return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
    }
    /**
     * Given a canvas label, attempt to go to that page. If no label was found.
     * the label will be attempted to match against the page index.
     *
     * @public
     * @params {string} label - The label to search on.
     * @params {?string} xAnchor - may either be "left", "right", or default "center"
     * @params {?string} yAnchor - may either be "top", "bottom", or default "center"
     * @returns {boolean} - True if the page index is valid; false if it is not.
     * */ gotoPageByLabel(label, xAnchor, yAnchor) {
        const pages = this.settings.manifest.pages;
        let llc = label.toLowerCase();
        for(let i = 0, len = pages.length; i < len; i++){
            if (pages[i].l.toLowerCase().indexOf(llc) > -1) {
                return this._gotoPageByIndex(i, xAnchor, yAnchor);
            }
        }
        const pageIndex = parseInt(label, 10) - 1;
        return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
    }
    /**
     * Jump to a page based on its URI.
     *
     * @public
     * @params {string} uri - The URI of the image to jump to.
     * @params {?string} xAnchor - may either be "left", "right", or default "center"
     * @params {?string} yAnchor - may either be "top", "bottom", or default "center"
     * @returns {boolean} true if successful and false if the URI is not found.
     */ gotoPageByURI(uri, xAnchor, yAnchor) {
        const pageIndex = this._getPageIndex(uri);
        return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
    }
    /**
     * Whether the page has other images to display.
     *
     * @public
     * @params {number} pageIndex - The 0-based page index
     * @returns {boolean} Whether the page has other images to display.
     **/ hasOtherImages(pageIndex) {
        return this.settings.manifest.pages[pageIndex].otherImages === true;
    }
    /**
     * Hides the pages that are marked "non-paged" in the IIIF manifest.
     *
     * @public
     **/ hideNonPagedPages() {
        this._reloadViewer({
            showNonPagedPages: false
        });
    }
    /**
     * Is the viewer currently in full-screen mode?
     *
     * @public
     * @returns {boolean} - Whether the viewer is in fullscreen mode.
     **/ isInFullscreen() {
        return this.settings.inFullscreen;
    }
    /**
     * Check if a page index is within the range of the document
     *
     * @public
     * @returns {boolean} - Whether the page index is valid.
     **/ isPageIndexValid(pageIndex) {
        return this._isPageIndexValid(pageIndex);
    }
    /**
     * Determines if a page is currently in the viewport
     *
     * @public
     * @params {number} pageIndex - The 0-based page index
     * @returns {boolean} - Whether the page is currently in the viewport.
     **/ isPageInViewport(pageIndex) {
        return this.viewerState.renderer.isPageVisible(pageIndex);
    }
    /**
     * Whether the Diva viewer has been fully initialized.
     *
     * @public
     * @returns {boolean} - True if the viewer is initialized; false otherwise.
     **/ isReady() {
        return this.viewerState.loaded;
    }
    /**
     * Check if something (e.g. a highlight box on a particular page) is visible
     *
     * @public
     * @params {number} pageIndex - The 0-based page index
     * @params {number} leftOffset - The distance of the region from the left of the viewport
     * @params {number} topOffset - The distance of the region from the top of the viewport
     * @params {number} width - The width of the region
     * @params {number} height - The height of the region
     * @returns {boolean} - Whether the region is in the viewport.
     **/ isRegionInViewport(pageIndex, leftOffset, topOffset, width, height) {
        const layout = this.divaState.viewerCore.getCurrentLayout();
        if (!layout) {
            return false;
        }
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
    /**
     * Whether the page layout is vertically or horizontally oriented.
     *
     * @public
     * @returns {boolean} - True if vertical; false if horizontal.
     **/ isVerticallyOriented() {
        return this.settings.verticallyOriented;
    }
    /**
     * Leave fullscreen mode if currently in fullscreen mode.
     *
     * @public
     * @returns {boolean} - true if in fullscreen mode intitially, false otherwise
     **/ leaveFullscreenMode() {
        if (this.settings.inFullscreen) {
            this._toggleFullscreen();
            return true;
        }
        return false;
    }
    /**
     * Leave grid view if currently in grid view.
     *
     * @public
     * @returns {boolean} - true if in grid view initially, false otherwise
     **/ leaveGridView() {
        if (this.settings.inGrid) {
            this._reloadViewer({
                inGrid: false
            });
            return true;
        }
        return false;
    }
    /**
     * Set the number of grid pages per row.
     *
     * @public
     * @params {number} pagesPerRow - The number of pages per row
     * @returns {boolean} - True if the operation was successful.
     **/ setGridPagesPerRow(pagesPerRow) {
        // TODO(wabain): Add test case
        if (!this.divaState.viewerCore.isValidOption('pagesPerRow', pagesPerRow)) {
            return false;
        }
        return this._reloadViewer({
            inGrid: true,
            pagesPerRow: pagesPerRow
        });
    }
    /**
     * Align this diva instance with a state object (as returned by getState)
     *
     * @public
     * @params {object} state - A Diva state object.
     * @returns {boolean} - True if the operation was successful.
     **/ setState(state) {
        return this._reloadViewer(this._getLoadOptionsForState(state));
    }
    /**
     * Sets the zoom level.
     *
     * @public
     * @returns {boolean} - True if the operation was successful.
     **/ setZoomLevel(zoomLevel) {
        if (this.settings.inGrid) {
            this._reloadViewer({
                inGrid: false
            });
        }
        return this.divaState.viewerCore.zoom(zoomLevel);
    }
    /**
     * Show non-paged pages.
     *
     * @public
     * @returns {boolean} - True if the operation was successful.
     **/ showNonPagedPages() {
        return this._reloadViewer({
            showNonPagedPages: true
        });
    }
    /**
     * Toggle fullscreen mode.
     *
     * @public
     * @returns {boolean} - True if the operation was successful.
     **/ toggleFullscreenMode() {
        this._toggleFullscreen();
    }
    /**
     * Show/Hide non-paged pages
     *
     * @public
     * @returns {boolean} - True if the operation was successful.
     **/ toggleNonPagedPagesVisibility() {
        return this._reloadViewer({
            showNonPagedPages: !this.settings.showNonPagedPages
        });
    }
    //Changes between horizontal layout and vertical layout. Returns true if document is now vertically oriented, false otherwise.
    toggleOrientation() {
        return this._togglePageLayoutOrientation();
    }
    /**
     * Translates a measurement from the zoom level on the largest size
     * to one on the current zoom level.
     *
     * For example, a point 1000 on an image that is on zoom level 2 of 5
     * translates to a position of 111.111... (1000 / (5 - 2)^2).
     *
     * Works for a single pixel co-ordinate or a dimension (e.g., translates a box
     * that is 1000 pixels wide on the original to one that is 111.111 pixels wide
     * on the current zoom level).
     *
     * @public
     * @params {number} position - A point on the max zoom level
     * @returns {number} - The same point on the current zoom level.
    */ translateFromMaxZoomLevel(position) {
        const zoomDifference = this.settings.maxZoomLevel - this.settings.zoomLevel;
        return position / Math.pow(2, zoomDifference);
    }
    /**
     * Translates a measurement from the current zoom level to the position on the
     * largest zoom level.
     *
     * Works for a single pixel co-ordinate or a dimension (e.g., translates a box
     * that is 111.111 pixels wide on the current image to one that is 1000 pixels wide
     * on the current zoom level).
     *
     * @public
     * @params {number} position - A point on the current zoom level
     * @returns {number} - The same point on the max zoom level.
    */ translateToMaxZoomLevel(position) {
        const zoomDifference = this.settings.maxZoomLevel - this.settings.zoomLevel;
        // if there is no difference, it's a box on the max zoom level and
        // we can just return the position.
        if (zoomDifference === 0) {
            return position;
        }
        return position * Math.pow(2, zoomDifference);
    }
    /**
     * Zoom in.
     *
     * @public
     * @returns {boolean} - false if it's at the maximum zoom
     **/ zoomIn() {
        return this.setZoomLevel(this.settings.zoomLevel + 1);
    }
    /**
     * Zoom out.
     * @returns {boolean} - false if it's at the minimum zoom
     **/ zoomOut() {
        return this.setZoomLevel(this.settings.zoomLevel - 1);
    }
    constructor(element, options){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__._)(this, "element", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__._)(this, "options", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__._)(this, "viewerState", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__._)(this, "settings", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__._)(this, "toolbar", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__._)(this, "hashState", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_9__._)(this, "divaState", void 0);
        /*
         * If a string is passed in, convert that to an element.
         * */ if (!(element instanceof HTMLElement)) {
            this.element = document.getElementById(element);
            if (this.element === null) {
                throw new _exceptions__WEBPACK_IMPORTED_MODULE_3__.DivaParentElementNotFoundException("The parent element was not found.");
            }
        }
        if (!options.objectData) {
            throw new _exceptions__WEBPACK_IMPORTED_MODULE_3__.ObjectDataNotSuppliedException('You must supply either a URL or a literal object to the `objectData` key.');
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
            pageAliasFunction: function() {
                return false;
            },
            pageLoadTimeout: 200,
            pagesPerRow: 5,
            requestHeaders: {
                "Accept": "application/json"
            },
            showNonPagedPages: false,
            throbberTimeout: 100,
            tileHeight: 256,
            tileWidth: 256,
            toolbarParentObject: null,
            verticallyOriented: true,
            viewportMargin: 200,
            zoomLevel: 2 // The initial zoom level (used to store the current zoom level)
        }, options);
        // In order to fill the height, use a wrapper div displayed using a flexbox layout
        const wrapperElement = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_2__.elt)('div', {
            class: `diva-wrapper${this.options.fillParentHeight ? " diva-wrapper-flexbox" : ""}`
        });
        this.element.appendChild(wrapperElement);
        this.options.toolbarParentObject = this.options.toolbarParentObject || wrapperElement;
        const viewerCore = new _viewer_core__WEBPACK_IMPORTED_MODULE_5__["default"](wrapperElement, this.options, this);
        this.viewerState = viewerCore.getInternalState();
        this.settings = viewerCore.getSettings();
        this.toolbar = this.settings.enableToolbar ? new _toolbar__WEBPACK_IMPORTED_MODULE_7__["default"](this) : null;
        wrapperElement.id = this.settings.ID + 'wrapper';
        this.divaState = {
            viewerCore: viewerCore,
            toolbar: this.toolbar
        };
        // only render the toolbar after the object has been loaded
        let handle = _diva_global__WEBPACK_IMPORTED_MODULE_4__["default"].Events.subscribe('ObjectDidLoad', ()=>{
            if (this.toolbar !== null) {
                this.toolbar.render();
            }
            _diva_global__WEBPACK_IMPORTED_MODULE_4__["default"].Events.unsubscribe(handle);
        });
        this.hashState = this._getHashParamState();
        this._loadOrFetchObjectData();
    }
}
Diva.Events = _diva_global__WEBPACK_IMPORTED_MODULE_4__["default"].Events;
/* ESM default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Diva);
/**
 * Make `Diva` available in the global context.
 * */ if (typeof window !== 'undefined') {
    (function(global) {
        global.Diva = global.Diva || Diva;
    })(window);
}


}),
"./source/js/document-handler.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (DocumentHandler)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _utils_maxby__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/maxby.ts");
/* ESM import */var _page_tools_overlay__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./source/js/page-tools-overlay.ts");



class DocumentHandler {
    // USER EVENTS
    onDoubleClick(event, coords) {
        const settings = this._viewerCore.getSettings();
        const newZoomLevel = event.ctrlKey ? settings.zoomLevel - 1 : settings.zoomLevel + 1;
        const position = this._viewerCore.getPagePositionAtViewportOffset(coords);
        this._viewerCore.zoom(newZoomLevel, position);
    }
    onPinch(_event, coords, startDistance, endDistance) {
        // FIXME: Do this check in a way which is less spaghetti code-y
        const viewerState = this._viewerCore.getInternalState();
        const settings = this._viewerCore.getSettings();
        let newZoomLevel = Math.log(Math.pow(2, settings.zoomLevel) * endDistance / (startDistance * Math.log(2))) / Math.log(2);
        newZoomLevel = Math.max(settings.minZoomLevel, newZoomLevel);
        newZoomLevel = Math.min(settings.maxZoomLevel, newZoomLevel);
        if (newZoomLevel === settings.zoomLevel) {
            return;
        }
        const position = this._viewerCore.getPagePositionAtViewportOffset(coords);
        const layout = this._viewerCore.getCurrentLayout();
        const centerOffset = layout.getPageToViewportCenterOffset(position.anchorPage, viewerState.viewport);
        const scaleRatio = 1 / Math.pow(2, settings.zoomLevel - newZoomLevel);
        this._viewerCore.reload({
            zoomLevel: newZoomLevel,
            goDirectlyTo: position.anchorPage,
            horizontalOffset: centerOffset.x - position.offset.left + position.offset.left * scaleRatio,
            verticalOffset: centerOffset.y - position.offset.top + position.offset.top * scaleRatio
        });
    }
    // VIEW EVENTS
    onViewWillLoad() {
        this._viewerCore.publish('DocumentWillLoad', this._viewerCore.getSettings());
    }
    onViewDidLoad() {
        // TODO: Should only be necessary to handle changes on view update, not
        // initial load
        this._handleZoomLevelChange();
        const currentPageIndex = this._viewerCore.getSettings().activePageIndex;
        const fileName = this._viewerCore.getPageName(currentPageIndex);
        this._viewerCore.publish("DocumentDidLoad", currentPageIndex, fileName);
    }
    onViewDidUpdate(renderedPages, targetPage) {
        const currentPage = targetPage !== null ? targetPage : getCentermostPage(renderedPages, this._viewerCore.getCurrentLayout(), this._viewerCore.getViewport());
        // calculate the visible pages from the rendered pages
        let temp = this._viewerState.viewport.intersectionTolerance;
        // without setting to 0, isPageVisible returns true for pages out of viewport by intersectionTolerance
        this._viewerState.viewport.intersectionTolerance = 0;
        let visiblePages = renderedPages.filter((index)=>this._viewerState.renderer.isPageVisible(index));
        // reset back to original value after getting true visible pages
        this._viewerState.viewport.intersectionTolerance = temp;
        // Don't change the current page if there is no page in the viewport
        // FIXME: Would be better to fall back to the page closest to the viewport
        if (currentPage !== null) {
            this._viewerCore.setCurrentPages(currentPage, visiblePages);
        }
        if (targetPage !== null) {
            this._viewerCore.publish("ViewerDidJump", targetPage);
        }
        this._handleZoomLevelChange();
    }
    _handleZoomLevelChange() {
        const viewerState = this._viewerState;
        const zoomLevel = viewerState.options.zoomLevel;
        // If this is not the initial load, trigger the zoom events
        if (viewerState.oldZoomLevel !== zoomLevel && viewerState.oldZoomLevel >= 0) {
            if (viewerState.oldZoomLevel < zoomLevel) {
                this._viewerCore.publish("ViewerDidZoomIn", zoomLevel);
            } else {
                this._viewerCore.publish("ViewerDidZoomOut", zoomLevel);
            }
            this._viewerCore.publish("ViewerDidZoom", zoomLevel);
        }
        viewerState.oldZoomLevel = zoomLevel;
    }
    destroy() {
        this._overlays.forEach((overlay)=>{
            this._viewerCore.removePageOverlay(overlay);
        }, this);
    }
    constructor(viewerCore){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_viewerCore", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_viewerState", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_overlays", void 0);
        this._viewerCore = viewerCore;
        this._viewerState = viewerCore.getInternalState();
        this._overlays = [];
        if (this._viewerCore.getPageTools().length) {
            const numPages = viewerCore.getSettings().numPages;
            for(let i = 0; i < numPages; i++){
                const overlay = new _page_tools_overlay__WEBPACK_IMPORTED_MODULE_1__["default"](i, viewerCore);
                this._overlays.push(overlay);
                this._viewerCore.addPageOverlay(overlay);
                // create dummy label for width calculation
                // this is necessary because the _pageToolsElem is only created on mount
                // so there's no other way to get its width before the pages are loaded
                // (which we need to avoid their width temporarily being 0 while loading)
                let dummyLabel = document.createElement('span');
                dummyLabel.innerHTML = viewerCore.settings.manifest.pages[i].l;
                dummyLabel.classList.add('diva-page-labels');
                dummyLabel.setAttribute('style', 'display: inline-block;');
                document.body.appendChild(dummyLabel);
                let labelWidth = dummyLabel.clientWidth;
                document.body.removeChild(dummyLabel);
                overlay.labelWidth = labelWidth;
            }
        }
    }
}

function getCentermostPage(renderedPages, layout, viewport) {
    const centerY = viewport.top + viewport.height / 2;
    const centerX = viewport.left + viewport.width / 2;
    // Find the minimum distance from the viewport center to a page.
    // Compute minus the squared distance from viewport center to the page's border.
    // http://gamedev.stackexchange.com/questions/44483/how-do-i-calculate-distance-between-a-point-and-an-axis-aligned-rectangle
    const centerPage = (0,_utils_maxby__WEBPACK_IMPORTED_MODULE_0__.maxBy)(renderedPages, (pageIndex)=>{
        const dims = layout.getPageDimensions(pageIndex);
        const imageOffset = layout.getPageOffset(pageIndex, {
            includePadding: true
        });
        const midX = imageOffset.left + dims.width / 2;
        const midY = imageOffset.top + dims.height / 2;
        const dx = Math.max(Math.abs(centerX - midX) - dims.width / 2, 0);
        const dy = Math.max(Math.abs(centerY - midY) - dims.height / 2, 0);
        return -(dx * dx + dy * dy);
    });
    return centerPage != null ? centerPage : null;
}


}),
"./source/js/document-layout.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (DocumentLayout)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/**
 * Translate page layouts, as generated by page-layouts, into an
 * object which computes layout information for the document as
 * a whole.
 */ 
class DocumentLayout {
    /**
     * @param pageIndex
     * @returns {PageInfo|null}
     */ getPageInfo(pageIndex) {
        return this._pageLookup[pageIndex] || null;
    }
    /**
     * Gets the page index of the first page so that we don't accidentally assume a first page index.
     * This is particularly useful when non-paged pages are skipped but we assume the default of 0
     * as the first page.
     * @returns {string}
     */ getIndexOfFirstPage() {
        return Object.keys(this._pageLookup)[0];
    }
    /**
     * Get the dimensions of a page
     *
     * @param pageIndex
     * @returns {{height: number, width: number}}
     */ getPageDimensions(pageIndex) {
        if (!this._pageLookup || !this._pageLookup[pageIndex]) {
            return null;
        }
        const region = getPageRegionFromPageInfo(this._pageLookup[pageIndex]);
        return {
            height: region.bottom - region.top,
            width: region.right - region.left
        };
    }
    // TODO(wabain): Get rid of this; it's a subset of the page region, so
    // give that instead
    /**
     * Get the top-left coordinates of a page, including*** padding
     *
     * @param pageIndex
     * @param options
     * @returns {{top: number, left: number} | null}
     */ getPageOffset(pageIndex, options) {
        const region = this.getPageRegion(pageIndex, options);
        if (!region) {
            return null;
        }
        return {
            top: region.top,
            left: region.left
        };
    }
    getPageRegion(pageIndex, options) {
        const pageInfo = this._pageLookup[pageIndex] || null;
        if (!pageInfo) {
            return null;
        }
        const region = getPageRegionFromPageInfo(pageInfo);
        const padding = pageInfo.group.padding;
        if (options && options.includePadding) {
            return {
                top: region.top + padding.top,
                left: region.left + padding.left,
                bottom: region.bottom,
                right: region.right
            };
        }
        return {
            top: region.top,
            left: region.left,
            // need to account for plugin icons below the page, see 
            // https://github.com/DDMAL/diva.js/issues/436
            bottom: region.bottom + padding.top,
            right: region.right
        };
    }
    /**
     * Get the distance from the top-right of the page to the center of the
     * specified viewport region
     *
     * @param pageIndex
     * @param viewport {{top: number, left: number, bottom: number, right: number}}
     * @returns {{x: number, y: number}}
     */ getPageToViewportCenterOffset(pageIndex, viewport) {
        const scrollLeft = viewport.left;
        const elementWidth = viewport.right - viewport.left;
        const offset = this.getPageOffset(pageIndex);
        if (!offset) {
            return null;
        }
        const x = scrollLeft - offset.left + Math.floor(elementWidth / 2);
        const scrollTop = viewport.top;
        const elementHeight = viewport.bottom - viewport.top;
        const y = scrollTop - offset.top + Math.floor(elementHeight / 2);
        return {
            x: x,
            y: y
        };
    }
    constructor(config, zoomLevel){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "dimensions", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "pageGroups", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_pageLookup", void 0);
        const computedLayout = getComputedLayout(config, zoomLevel);
        this.dimensions = computedLayout.dimensions;
        this.pageGroups = computedLayout.pageGroups;
        this._pageLookup = getPageLookup(computedLayout.pageGroups);
    }
}

function getPageRegionFromPageInfo(page) {
    const top = page.groupOffset.top + page.group.region.top;
    const bottom = top + page.dimensions.height;
    const left = page.groupOffset.left + page.group.region.left;
    const right = left + page.dimensions.width;
    return {
        top: top,
        bottom: bottom,
        left: left,
        right: right
    };
}
function getPageLookup(pageGroups) {
    const pageLookup = {};
    pageGroups.forEach((group)=>{
        group.pages.forEach((page)=>{
            pageLookup[page.index] = {
                index: page.index,
                group: group,
                dimensions: page.dimensions,
                groupOffset: page.groupOffset
            };
        });
    });
    return pageLookup;
}
function getComputedLayout(config, zoomLevel) {
    const scaledLayouts = zoomLevel === null ? config.pageLayouts : getScaledPageLayouts(config, zoomLevel);
    const documentSecondaryExtent = getExtentAlongSecondaryAxis(config, scaledLayouts);
    // The current position in the document along the primary axis
    let primaryDocPosition = config.verticallyOriented ? config.padding.document.top : config.padding.document.left;
    const pageGroups = [];
    // TODO: Use bottom, right as well
    const pagePadding = {
        top: config.padding.page.top,
        left: config.padding.page.left
    };
    scaledLayouts.forEach((layout, index)=>{
        let top, left;
        if (config.verticallyOriented) {
            top = primaryDocPosition;
            left = (documentSecondaryExtent - layout.dimensions.width) / 2;
        } else {
            top = (documentSecondaryExtent - layout.dimensions.height) / 2;
            left = primaryDocPosition;
        }
        const region = {
            top: top,
            bottom: top + pagePadding.top + layout.dimensions.height,
            left: left,
            right: left + pagePadding.left + layout.dimensions.width
        };
        pageGroups.push({
            index: index,
            dimensions: layout.dimensions,
            pages: layout.pages,
            region: region,
            padding: pagePadding
        });
        primaryDocPosition = config.verticallyOriented ? region.bottom : region.right;
    });
    let height, width;
    if (config.verticallyOriented) {
        height = primaryDocPosition + pagePadding.top;
        width = documentSecondaryExtent;
    } else {
        height = documentSecondaryExtent;
        width = primaryDocPosition + pagePadding.left;
    }
    return {
        dimensions: {
            height: height,
            width: width
        },
        pageGroups: pageGroups
    };
}
function getScaledPageLayouts(config, zoomLevel) {
    const scaleRatio = Math.pow(2, zoomLevel - config.maxZoomLevel);
    return config.pageLayouts.map((group)=>({
            dimensions: scaleDimensions(group.dimensions, scaleRatio),
            pages: group.pages.map((page)=>({
                    index: page.index,
                    groupOffset: {
                        top: Math.floor(page.groupOffset.top * scaleRatio),
                        left: Math.floor(page.groupOffset.left * scaleRatio)
                    },
                    dimensions: scaleDimensions(page.dimensions, scaleRatio)
                }))
        }));
}
function scaleDimensions(dimensions, scaleRatio) {
    return {
        height: Math.floor(dimensions.height * scaleRatio),
        width: Math.floor(dimensions.width * scaleRatio)
    };
}
function getExtentAlongSecondaryAxis(config, scaledLayouts) {
    // Get the extent of the document along the secondary axis
    let secondaryDim, secondaryPadding;
    const docPadding = config.padding.document;
    if (config.verticallyOriented) {
        secondaryDim = 'width';
        secondaryPadding = docPadding.left + docPadding.right;
    } else {
        secondaryDim = 'height';
        secondaryPadding = docPadding.top + docPadding.bottom;
    }
    return secondaryPadding + scaledLayouts.reduce((maxDim, layout)=>Math.max(layout.dimensions[secondaryDim], maxDim), 0);
}


}),
"./source/js/exceptions.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  DivaParentElementNotFoundException: () => (DivaParentElementNotFoundException),
  NotAnIIIFManifestException: () => (NotAnIIIFManifestException),
  ObjectDataNotSuppliedException: () => (ObjectDataNotSuppliedException)
});
function DivaParentElementNotFoundException(message) {
    this.name = "DivaParentElementNotFoundException";
    this.message = message;
    this.stack = new Error().stack;
}
DivaParentElementNotFoundException.prototype = new Error();
function NotAnIIIFManifestException(message) {
    this.name = "NotAnIIIFManifestException";
    this.message = message;
    this.stack = new Error().stack;
}
NotAnIIIFManifestException.prototype = new Error();
function ObjectDataNotSuppliedException(message) {
    this.name = "ObjectDataNotSuppliedException";
    this.message = message;
    this.stack = new Error().stack;
}
ObjectDataNotSuppliedException.prototype = new Error();


}),
"./source/js/gesture-events.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__WEBPACK_DEFAULT_EXPORT__)
});
/* ESM default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
    onDoubleClick,
    onPinch,
    onDoubleTap
});
const DOUBLE_CLICK_TIMEOUT = 500;
const DOUBLE_TAP_DISTANCE_THRESHOLD = 50;
const DOUBLE_TAP_TIMEOUT = 250;
function onDoubleClick(elem, callback) {
    elem.addEventListener('dblclick', function(event) {
        if (!event.ctrlKey) {
            callback(event, getRelativeOffset(event.currentTarget, event));
        }
    });
    // Handle the control key for macs (in conjunction with double-clicking)
    // FIXME: Does a click get handled with ctrl pressed on non-Macs?
    const tracker = createDoubleEventTracker(DOUBLE_CLICK_TIMEOUT);
    elem.addEventListener('contextmenu', function(event) {
        event.preventDefault();
        if (event.ctrlKey) {
            if (tracker.isTriggered()) {
                tracker.reset();
                callback(event, getRelativeOffset(event.currentTarget, event));
            } else {
                tracker.trigger();
            }
        }
    });
}
function onPinch(elem, callback) {
    let startDistance = 0;
    elem.addEventListener('touchstart', function(event) {
        // Prevent mouse event from firing
        event.preventDefault();
        if (event.touches.length === 2) {
            startDistance = distance(event.touches[0].clientX, event.touches[0].clientY, event.touches[1].clientX, event.touches[1].clientY);
        }
    });
    elem.addEventListener('touchmove', function(event) {
        // Prevent mouse event from firing
        event.preventDefault();
        if (event.touches.length === 2) {
            const touches = event.touches;
            const moveDistance = distance(touches[0].clientX, touches[0].clientY, touches[1].clientX, touches[1].clientY);
            const zoomDelta = moveDistance - startDistance;
            if (Math.abs(zoomDelta) > 0) {
                const touchCenter = {
                    pageX: (touches[0].clientX + touches[1].clientX) / 2,
                    pageY: (touches[0].clientY + touches[1].clientY) / 2
                };
                callback(event, getRelativeOffset(event.currentTarget, touchCenter), startDistance, moveDistance);
            }
        }
    });
}
function onDoubleTap(elem, callback) {
    const tracker = createDoubleEventTracker(DOUBLE_TAP_TIMEOUT);
    let firstTap = null;
    elem.addEventListener('touchend', (event)=>{
        // Prevent mouse event from firing
        event.preventDefault();
        if (tracker.isTriggered()) {
            tracker.reset();
            // Doubletap has occurred
            const secondTap = {
                pageX: event.changedTouches[0].clientX,
                pageY: event.changedTouches[0].clientY
            };
            // If first tap is close to second tap (prevents interference with scale event)
            const tapDistance = distance(firstTap.pageX, firstTap.pageY, secondTap.pageX, secondTap.pageY);
            // TODO: Could give something higher-level than secondTap to callback
            if (tapDistance < DOUBLE_TAP_DISTANCE_THRESHOLD) {
                callback(event, getRelativeOffset(event.currentTarget, secondTap));
            }
            firstTap = null;
        } else {
            firstTap = {
                pageX: event.changedTouches[0].clientX,
                pageY: event.changedTouches[0].clientY
            };
            tracker.trigger();
        }
    });
}
// Pythagorean theorem to get the distance between two points (used for
// calculating finger distance for double-tap and pinch-zoom)
function distance(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}
// Utility to keep track of whether an event has been triggered twice
// during a a given duration
function createDoubleEventTracker(timeoutDuration) {
    let triggered = false;
    let timeoutId = null;
    return {
        trigger () {
            triggered = true;
            resetTimeout();
            timeoutId = setTimeout(function() {
                triggered = false;
                timeoutId = null;
            }, timeoutDuration);
        },
        isTriggered () {
            return triggered;
        },
        reset () {
            triggered = false;
            resetTimeout();
        }
    };
    function resetTimeout() {
        if (timeoutId !== null) {
            clearTimeout(timeoutId);
            timeoutId = null;
        }
    }
}
function getRelativeOffset(elem, pageCoords) {
    const bounds = elem.getBoundingClientRect();
    return {
        left: pageCoords.pageX - bounds.left,
        top: pageCoords.pageY - bounds.top
    };
}


}),
"./source/js/grid-handler.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (GridHandler)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _utils_maxby__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/maxby.ts");


class GridHandler {
    // USER EVENTS
    onDoubleClick(_event, coords) {
        const position = this._viewerCore.getPagePositionAtViewportOffset(coords);
        const layout = this._viewerCore.getCurrentLayout();
        const viewport = this._viewerCore.getViewport();
        const pageToViewportCenterOffset = layout.getPageToViewportCenterOffset(position.anchorPage, viewport);
        this._viewerCore.reload({
            inGrid: false,
            goDirectlyTo: position.anchorPage,
            horizontalOffset: pageToViewportCenterOffset.x + position.offset.left,
            verticalOffset: pageToViewportCenterOffset.y + position.offset.top
        });
    }
    onPinch() {
        this._viewerCore.reload({
            inGrid: false
        });
    }
    // VIEW EVENTS
    onViewWillLoad() {
    // FIXME(wabain): Should something happen here?
    /* No-op */ }
    onViewDidLoad() {
    // FIXME(wabain): Should something happen here?
    /* No-op */ }
    onViewDidUpdate(renderedPages, targetPage) {
        // return early if there are no rendered pages in view.
        if (renderedPages.length === 0) {
            return;
        }
        // calculate the visible pages from the rendered pages
        let temp = this._viewerCore.viewerState.viewport.intersectionTolerance;
        // without setting to 0, isPageVisible returns true for pages out of viewport by intersectionTolerance
        this._viewerCore.viewerState.viewport.intersectionTolerance = 0;
        let visiblePages = renderedPages.filter((index)=>this._viewerCore.viewerState.renderer.isPageVisible(index));
        // reset back to original value after getting true visible pages
        this._viewerCore.viewerState.viewport.intersectionTolerance = temp;
        if (targetPage !== null) {
            this._viewerCore.setCurrentPages(targetPage, visiblePages);
            return;
        }
        // Select the current page from the first row if it is fully visible, or from
        // the second row if it is fully visible, or from the centermost row otherwise.
        // If the current page is in that group then don't change it. Otherwise, set
        // the current page to the group's first page.
        const layout = this._viewerCore.getCurrentLayout();
        const groups = [];
        renderedPages.forEach((pageIndex)=>{
            const group = layout.getPageInfo(pageIndex).group;
            if (groups.length === 0 || group !== groups[groups.length - 1]) {
                groups.push(group);
            }
        });
        const viewport = this._viewerCore.getViewport();
        let chosenGroup;
        if (groups.length === 1 || groups[0].region.top >= viewport.top) {
            chosenGroup = groups[0];
        } else if (groups[1].region.bottom <= viewport.bottom) {
            chosenGroup = groups[1];
        } else {
            chosenGroup = getCentermostGroup(groups, viewport);
        }
        const currentPage = this._viewerCore.getSettings().activePageIndex;
        const hasCurrentPage = chosenGroup.pages.some((page)=>page.index === currentPage);
        if (!hasCurrentPage) {
            this._viewerCore.setCurrentPages(chosenGroup.pages[0].index, visiblePages);
        }
    }
    destroy() {
    // No-op
    }
    constructor(viewerCore){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_viewerCore", void 0);
        this._viewerCore = viewerCore;
    }
}

function getCentermostGroup(groups, viewport) {
    const viewportMiddle = viewport.top + viewport.height / 2;
    return (0,_utils_maxby__WEBPACK_IMPORTED_MODULE_0__.maxBy)(groups, (group)=>{
        const groupMiddle = group.region.top + group.dimensions.height / 2;
        return -Math.abs(viewportMiddle - groupMiddle);
    });
}


}),
"./source/js/iiif-source-adapter.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (IIIFSourceAdapter)
});
class IIIFSourceAdapter {
    getPageImageURL(manifest, pageIndex, size) {
        let dimens;
        if (!size || size.width == null && size.height == null) {
            dimens = 'full';
        } else {
            dimens = (size.width == null ? '' : size.width) + ',' + (size.height == null ? '' : size.height);
        }
        const page = manifest.pages[pageIndex];
        const quality = page.api > 1.1 ? 'default' : 'native';
        return encodeURI(page.url + 'full/' + dimens + '/0/' + quality + '.jpg');
    }
    getTileImageURL(manifest, pageIndex, params) {
        const page = manifest.pages[pageIndex];
        let height, width;
        if (params.row === params.rowCount - 1) {
            height = page.d[params.zoomLevel].h - (params.rowCount - 1) * params.tileDimensions.height;
        } else {
            height = params.tileDimensions.height;
        }
        if (params.col === params.colCount - 1) {
            width = page.d[params.zoomLevel].w - (params.colCount - 1) * params.tileDimensions.width;
        } else {
            width = params.tileDimensions.width;
        }
        const zoomDifference = Math.pow(2, manifest.maxZoom - params.zoomLevel);
        let x = params.col * params.tileDimensions.width * zoomDifference;
        let y = params.row * params.tileDimensions.height * zoomDifference;
        if (page.hasOwnProperty('xoffset')) {
            x += page.xoffset;
            y += page.yoffset;
        }
        const region = [
            x,
            y,
            width * zoomDifference,
            height * zoomDifference
        ].join(',');
        const quality = page.api > 1.1 ? 'default' : 'native';
        return encodeURI(page.url + region + '/' + width + ',' + height + '/0/' + quality + '.jpg');
    }
}



}),
"./source/js/image-cache.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (ImageCache)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");

const debug = __webpack_require__("./node_modules/debug/src/browser.js")('diva:ImageCache');
/* FIXME(wabain): The caching strategy here is completely
 * arbitrary and the implementation isn't especially efficient.
 */ const DEFAULT_MAX_KEYS = 100;
class ImageCache {
    get(url) {
        const record = this._urls[url];
        return record ? record.img : null;
    }
    has(url) {
        return !!this._urls[url];
    }
    put(url, img) {
        let record = this._urls[url];
        if (record) {
            // FIXME: Does this make sense for this use case?
            record.img = img;
            this._promote(record);
        } else {
            record = {
                img: img,
                url: url
            };
            this._urls[url] = record;
            this._tryEvict(1);
            this._lru.unshift(record);
        }
    }
    _promote(record) {
        const index = this._lru.indexOf(record);
        this._lru.splice(index, 1);
        this._lru.unshift(record);
    }
    _tryEvict(extraCapacity) {
        const allowedEntryCount = this.maxKeys - extraCapacity;
        if (this._lru.length <= allowedEntryCount) {
            return;
        }
        let evictionIndex = this._lru.length - 1;
        for(;;){
            const target = this._lru[evictionIndex];
            if (!this._held[target.url]) {
                debug('Evicting image %s', target.url);
                this._lru.splice(evictionIndex, 1);
                delete this._urls[target.url];
                if (this._lru.length <= allowedEntryCount) break;
            }
            if (evictionIndex === 0) {
                /* istanbul ignore next */ debug.enabled && debug('Cache overfull by %s (all entries are being held)', this._lru.length - allowedEntryCount);
                break;
            }
            evictionIndex--;
        }
    }
    acquire(url) {
        this._held[url] = (this._held[url] || 0) + 1;
        this._promote(this._urls[url]);
    }
    release(url) {
        const count = this._held[url];
        if (count > 1) {
            this._held[url]--;
        } else {
            delete this._held[url];
        }
        this._tryEvict(0);
    }
    constructor(options){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "maxKeys", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_held", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_urls", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_lru", void 0);
        options = options || {
            maxKeys: DEFAULT_MAX_KEYS
        };
        this.maxKeys = options.maxKeys || DEFAULT_MAX_KEYS;
        this._held = {};
        this._urls = {};
        this._lru = [];
    }
}



}),
"./source/js/image-manifest.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (ImageManifest)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _parse_iiif_manifest__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/parse-iiif-manifest.ts");
/* ESM import */var _iiif_source_adapter__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./source/js/iiif-source-adapter.ts");



class ImageManifest {
    static fromIIIF(iiifManifest) {
        const data = (0,_parse_iiif_manifest__WEBPACK_IMPORTED_MODULE_0__["default"])(iiifManifest);
        return new ImageManifest(data, new _iiif_source_adapter__WEBPACK_IMPORTED_MODULE_1__["default"]());
    }
    isPageValid(pageIndex, showNonPagedPages) {
        if (!showNonPagedPages && this.paged && !this.pages[pageIndex].paged) {
            return false;
        }
        return pageIndex >= 0 && pageIndex < this.pages.length;
    }
    getMaxPageDimensions(pageIndex) {
        const maxDims = this.pages[pageIndex].d[this.maxZoom];
        return {
            height: maxDims.h,
            width: maxDims.w
        };
    }
    getPageDimensionsAtZoomLevel(pageIndex, zoomLevel) {
        const maxDims = this.pages[pageIndex].d[this.maxZoom];
        const scaleRatio = getScaleRatio(this.maxZoom, zoomLevel);
        return {
            height: maxDims.h * scaleRatio,
            width: maxDims.w * scaleRatio
        };
    }
    /**
     * Returns a URL for the image of the given page. The optional size
     * parameter supports setting the image width or height (default is
     * full-sized).
     */ getPageImageURL(pageIndex, size) {
        return this._urlAdapter.getPageImageURL(this, pageIndex, size);
    }
    /**
     * Return an array of tile objects for the specified page and integer zoom level
     */ getPageImageTiles(pageIndex, zoomLevel, tileDimensions) {
        const page = this.pages[pageIndex];
        if (!isFinite(zoomLevel) || zoomLevel % 1 !== 0) {
            throw new TypeError('Zoom level must be an integer: ' + zoomLevel);
        }
        const rows = Math.ceil(page.d[zoomLevel].h / tileDimensions.height);
        const cols = Math.ceil(page.d[zoomLevel].w / tileDimensions.width);
        const tiles = [];
        let row, col, url;
        for(row = 0; row < rows; row++){
            for(col = 0; col < cols; col++){
                url = this._urlAdapter.getTileImageURL(this, pageIndex, {
                    row: row,
                    col: col,
                    rowCount: rows,
                    colCount: cols,
                    zoomLevel: zoomLevel,
                    tileDimensions: tileDimensions
                });
                // FIXME: Dimensions should account for partial tiles (e.g. the
                // last row and column in a tiled image)
                tiles.push({
                    row: row,
                    col: col,
                    zoomLevel: zoomLevel,
                    dimensions: {
                        height: tileDimensions.height,
                        width: tileDimensions.width
                    },
                    offset: {
                        top: row * tileDimensions.height,
                        left: col * tileDimensions.width
                    },
                    url: url
                });
            }
        }
        return {
            zoomLevel: zoomLevel,
            rows: rows,
            cols: cols,
            tiles: tiles
        };
    }
    getAverageWidth(zoomLevel) {
        return this._averageWidths[zoomLevel];
    }
    getAverageHeight(zoomLevel) {
        return this._averageHeights[zoomLevel];
    }
    getMaxWidth(zoomLevel) {
        return this._maxWidths[zoomLevel];
    }
    getMaxHeight(zoomLevel) {
        return this._maxHeights[zoomLevel];
    }
    getTotalWidth(zoomLevel) {
        return this._totalWidths[zoomLevel];
    }
    getTotalHeight(zoomLevel) {
        return this._totalHeights[zoomLevel];
    }
    constructor(data, urlAdapter){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "pages", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "maxZoom", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "maxRatio", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "minRatio", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "itemTitle", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "metadata", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "paged", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_maxWidths", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_maxHeights", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_averageWidths", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_averageHeights", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_totalHeights", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_totalWidths", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "_urlAdapter", void 0);
        // Save all the data we need
        this.pages = data.pgs;
        this.maxZoom = data.max_zoom;
        this.maxRatio = data.dims.max_ratio;
        this.minRatio = data.dims.min_ratio;
        this.itemTitle = data.item_title;
        this.metadata = data.metadata;
        // Only given for IIIF manifests
        this.paged = data.paged;
        // These are arrays, the index corresponding to the zoom level
        this._maxWidths = data.dims.max_w;
        this._maxHeights = data.dims.max_h;
        this._averageWidths = data.dims.a_wid;
        this._averageHeights = data.dims.a_hei;
        this._totalHeights = data.dims.t_hei;
        this._totalWidths = data.dims.t_wid;
        this._urlAdapter = urlAdapter;
    }
}

function getScaleRatio(sourceZoomLevel, targetZoomLevel) {
    return 1 / Math.pow(2, sourceZoomLevel - targetZoomLevel);
}


}),
"./source/js/image-request-handler.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (ImageRequestHandler)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");

class ImageRequestHandler {
    abort() {
        clearTimeout(this.timeout);
        // FIXME
        // People on the Internet say that doing this {{should/should not}} abort the request. I believe
        // it corresponds to what the WHATWG HTML spec says should happen when the UA
        // updates the image data if selected source is null.
        //
        // Sources:
        //
        // https://html.spec.whatwg.org/multipage/embedded-content.html#the-img-element
        // http://stackoverflow.com/questions/7390888/does-changing-the-src-attribute-of-an-image-stop-the-image-from-downloading
        if (this._image) {
            this._image.onload = this._image.onerror = null;
            this._image.src = '';
        }
        this._aborted = true;
    }
    _handleLoad() {
        if (this._aborted) {
            console.error('ImageRequestHandler invoked on cancelled request for ' + this._url);
            return;
        }
        if (this._complete) {
            console.error('ImageRequestHandler invoked on completed request for ' + this._url);
            return;
        }
        this._complete = true;
        this._callback(this._image);
    }
    _handleError() {
        this._errorCallback(this._image);
    }
    constructor(options){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_image", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_callback", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_errorCallback", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "timeout", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "timeoutTime", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_aborted", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_crossOrigin", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_url", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_complete", void 0);
        this._url = options.url;
        this._callback = options.load;
        this._errorCallback = options.error;
        this.timeoutTime = options.timeoutTime || 0;
        this._aborted = this._complete = false;
        this._crossOrigin = options.settings.imageCrossOrigin;
        //Use a timeout to allow the requests to be debounced (as they are in renderer)
        this.timeout = setTimeout(()=>{
            // Initiate the request
            this._image = new Image();
            this._image.crossOrigin = this._crossOrigin;
            this._image.onload = this._handleLoad.bind(this);
            this._image.onerror = this._handleError.bind(this);
            this._image.src = options.url;
        }, this.timeoutTime);
    }
}
/**
 * Handler for the request for an image tile
 *
 * @param url
 * @param callback
 * @constructor
 */ 


}),
"./source/js/interpolate-animation.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__WEBPACK_DEFAULT_EXPORT__)
});
// TODO: requestAnimationFrame fallback
/* ESM default export */ const __WEBPACK_DEFAULT_EXPORT__ = ({
    animate,
    easing: {
        linear: linearEasing,
        cubic: inOutCubicEasing
    }
});
let now = ()=>{
    return performance.now();
};
function animate(options) {
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
    const paramKeys = Object.keys(parameters);
    paramKeys.forEach((key)=>{
        const config = parameters[key];
        tweenFns[key] = interpolate(config.from, config.to, config.easing || inOutCubicEasing);
    });
    // Run it!
    let requestId = requestAnimationFrame(update);
    return {
        cancel () {
            if (requestId !== null) {
                cancelAnimationFrame(requestId);
                handleAnimationCompletion({
                    interrupted: true
                });
            }
        }
    };
    function update() {
        const current = now();
        const elapsed = Math.min((current - start) / durationMs, 1);
        updateValues(elapsed);
        onUpdate(values);
        if (current < end) {
            requestId = requestAnimationFrame(update);
        } else {
            handleAnimationCompletion({
                interrupted: false
            });
        }
    }
    function updateValues(elapsed) {
        paramKeys.forEach((key)=>{
            values[key] = tweenFns[key](elapsed);
        });
    }
    function handleAnimationCompletion(info) {
        requestId = null;
        if (onEnd) {
            onEnd(info);
        }
    }
}
function interpolate(start, end, easing) {
    return (elapsed)=>{
        return start + (end - start) * easing(elapsed);
    };
}
/**
 * Easing functions. inOutCubicEasing is the default, but
 * others are given for convenience.
 *
 **/ function linearEasing(e) {
    return e;
}
/* jshint ignore:start */ function inOutQuadEasing(e) {
    return e < .5 ? 2 * e * e : -1 + (4 - 2 * e) * e;
}
/* jshint ignore:end */ function inOutCubicEasing(t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
}


}),
"./source/js/page-layouts/book-layout.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (getBookLayoutGroups)
});
/* ESM import */var _page_dimensions__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/page-layouts/page-dimensions.ts");

function getBookLayoutGroups(viewerConfig) {
    const groupings = getGroupings(viewerConfig);
    return groupings.map((grouping)=>getGroupLayoutsFromPageGrouping(viewerConfig, grouping));
}
function getGroupings(viewerConfig) {
    const manifest = viewerConfig.manifest;
    const pagesByGroup = [];
    let leftPage = null;
    let nonPagedPages = []; // Pages to display below the current group
    const _addNonPagedPages = ()=>{
        for(let i = 0, nlen = nonPagedPages.length; i < nlen; i++){
            pagesByGroup.push([
                nonPagedPages[i]
            ]);
        }
        nonPagedPages = [];
    };
    manifest.pages.forEach((page, index)=>{
        const pageRecord = {
            index: index,
            dimensions: (0,_page_dimensions__WEBPACK_IMPORTED_MODULE_0__["default"])(index, manifest),
            paged: !manifest.paged || page.paged
        };
        // Only display non-paged pages if specified in the settings
        if (!viewerConfig.showNonPagedPages && !pageRecord.paged) {
            return;
        }
        if (!pageRecord.paged) {
            nonPagedPages.push(pageRecord);
        } else if (index === 0 || page.facingPages) {
            // The first page is placed on its own
            pagesByGroup.push([
                pageRecord
            ]);
            _addNonPagedPages();
        } else if (leftPage === null) {
            leftPage = pageRecord;
        } else {
            pagesByGroup.push([
                leftPage,
                pageRecord
            ]);
            leftPage = null;
            _addNonPagedPages();
        }
    });
    // Flush a final left page
    if (leftPage !== null) {
        pagesByGroup.push([
            leftPage
        ]);
        _addNonPagedPages();
    }
    return pagesByGroup;
}
function getGroupLayoutsFromPageGrouping(viewerConfig, grouping) {
    const verticallyOriented = viewerConfig.verticallyOriented;
    if (grouping.length === 2) {
        return getFacingPageGroup(grouping[0], grouping[1], verticallyOriented);
    }
    const page = grouping[0];
    const pageDims = page.dimensions;
    // The first page is placed on its own to the right in vertical orientation.
    // NB that this needs to be the page with index 0; if the first page is excluded
    // from the layout then this special case shouldn't apply.
    // If the page is tagged as 'non-paged', center it horizontally
    let leftOffset;
    if (page.paged) {
        leftOffset = page.index === 0 && verticallyOriented ? pageDims.width : 0;
    } else {
        leftOffset = verticallyOriented ? pageDims.width / 2 : 0;
    }
    const shouldBeHorizontallyAdjusted = verticallyOriented && !viewerConfig.manifest.pages[page.index].facingPages;
    // We need to left-align the page in vertical orientation, so we double
    // the group width
    return {
        dimensions: {
            height: pageDims.height,
            width: shouldBeHorizontallyAdjusted ? pageDims.width * 2 : pageDims.width
        },
        pages: [
            {
                index: page.index,
                groupOffset: {
                    top: 0,
                    left: leftOffset
                },
                dimensions: pageDims
            }
        ]
    };
}
function getFacingPageGroup(leftPage, rightPage, verticallyOriented) {
    const leftDims = leftPage.dimensions;
    const rightDims = rightPage.dimensions;
    const height = Math.max(leftDims.height, rightDims.height);
    let width, firstLeftOffset, secondLeftOffset;
    if (verticallyOriented) {
        const midWidth = Math.max(leftDims.width, rightDims.width);
        width = midWidth * 2;
        firstLeftOffset = midWidth - leftDims.width;
        secondLeftOffset = midWidth;
    } else {
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


}),
"./source/js/page-layouts/grid-layout.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (getGridLayoutGroups)
});
function getGridLayoutGroups(viewerConfig) {
    const viewportWidth = viewerConfig.viewport.width;
    const manifest = viewerConfig.manifest;
    const pagesPerRow = viewerConfig.pagesPerRow;
    const fixedHeightGrid = viewerConfig.fixedHeightGrid;
    const fixedPadding = viewerConfig.fixedPadding;
    const showNonPagedPages = viewerConfig.showNonPagedPages;
    const horizontalPadding = fixedPadding * (pagesPerRow + 1);
    const pageWidth = (viewportWidth - horizontalPadding) / pagesPerRow;
    const gridPageWidth = pageWidth;
    // Calculate the row height depending on whether we want to fix the width or the height
    const rowHeight = fixedHeightGrid ? fixedPadding + manifest.minRatio * pageWidth : fixedPadding + manifest.maxRatio * pageWidth;
    const groups = [];
    let currentPages = [];
    const getGridPageDimensions = (pageData)=>{
        // Calculate the width, height and horizontal placement of this page
        // Get dimensions at max zoom level, although any level should be fine
        const pageDimenData = pageData.d[pageData.d.length - 1];
        const heightToWidthRatio = pageDimenData.h / pageDimenData.w;
        let pageWidth, pageHeight;
        if (fixedHeightGrid) {
            pageWidth = (rowHeight - fixedPadding) / heightToWidthRatio;
            pageHeight = rowHeight - fixedPadding;
        } else {
            pageWidth = gridPageWidth;
            pageHeight = pageWidth * heightToWidthRatio;
        }
        return {
            width: Math.round(pageWidth),
            height: Math.round(pageHeight)
        };
    };
    const rowDimensions = {
        height: rowHeight,
        width: viewportWidth
    };
    manifest.pages.forEach((page, pageIndex)=>{
        if (!showNonPagedPages && manifest.paged && !page.paged) {
            return;
        }
        // Calculate the width, height and horizontal placement of this page
        const pageDimens = getGridPageDimensions(page);
        let leftOffset = Math.floor(currentPages.length * (fixedPadding + gridPageWidth) + fixedPadding);
        // Center the page if the height is fixed (otherwise, there is no horizontal padding)
        if (fixedHeightGrid) {
            leftOffset += (gridPageWidth - pageDimens.width) / 2;
        }
        // TODO: Precompute page dimensions everywhere
        currentPages.push({
            index: pageIndex,
            dimensions: pageDimens,
            groupOffset: {
                top: 0,
                left: leftOffset
            }
        });
        if (currentPages.length === pagesPerRow) {
            groups.push({
                dimensions: rowDimensions,
                pages: currentPages
            });
            currentPages = [];
        }
    });
    if (currentPages.length > 0) {
        groups.push({
            dimensions: rowDimensions,
            pages: currentPages
        });
    }
    return groups;
}


}),
"./source/js/page-layouts/index.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (getPageLayouts)
});
/* ESM import */var _book_layout__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/page-layouts/book-layout.ts");
/* ESM import */var _singles_layout__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./source/js/page-layouts/singles-layout.ts");
/* ESM import */var _grid_layout__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__("./source/js/page-layouts/grid-layout.ts");



/** Get the relative positioning of pages for the current view */ function getPageLayouts(settings) {
    if (settings.inGrid) {
        return (0,_grid_layout__WEBPACK_IMPORTED_MODULE_2__["default"])(pluck(settings, [
            'manifest',
            'viewport',
            'pagesPerRow',
            'fixedHeightGrid',
            'fixedPadding',
            'showNonPagedPages'
        ]));
    } else {
        const config = pluck(settings, [
            'manifest',
            'verticallyOriented',
            'showNonPagedPages'
        ]);
        if (settings.inBookLayout) {
            return (0,_book_layout__WEBPACK_IMPORTED_MODULE_0__["default"])(config);
        } else {
            return (0,_singles_layout__WEBPACK_IMPORTED_MODULE_1__["default"])(config);
        }
    }
}
function pluck(obj, keys) {
    const out = {};
    keys.forEach(function(key) {
        out[key] = obj[key];
    });
    return out;
}


}),
"./source/js/page-layouts/page-dimensions.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (getPageDimensions)
});
function getPageDimensions(pageIndex, manifest) {
    const dims = manifest.getMaxPageDimensions(pageIndex);
    return {
        width: Math.floor(dims.width),
        height: Math.floor(dims.height)
    };
}


}),
"./source/js/page-layouts/singles-layout.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (getSinglesLayoutGroups)
});
/* ESM import */var _page_dimensions__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/page-layouts/page-dimensions.ts");

function getSinglesLayoutGroups(viewerConfig) {
    const manifest = viewerConfig.manifest;
    // Render each page alone in a group
    const pages = [];
    manifest.pages.forEach((page, index)=>{
        if (!viewerConfig.showNonPagedPages && manifest.paged && !page.paged) {
            return;
        }
        const pageDims = (0,_page_dimensions__WEBPACK_IMPORTED_MODULE_0__["default"])(index, manifest);
        pages.push({
            dimensions: pageDims,
            pages: [
                {
                    index: index,
                    groupOffset: {
                        top: 0,
                        left: 0
                    },
                    dimensions: pageDims
                }
            ]
        });
    });
    return pages;
}


}),
"./source/js/page-overlay-manager.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (PageOverlayManager)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
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
class PageOverlayManager {
    addOverlay(overlay) {
        const overlaysByPage = this._pages[overlay.page] || (this._pages[overlay.page] = []);
        overlaysByPage.push(overlay);
        if (this._renderedPageMap[overlay.page]) {
            overlay.mount();
        }
    }
    removeOverlay(overlay) {
        const page = overlay.page;
        const overlaysByPage = this._pages[page];
        if (!overlaysByPage) {
            return;
        }
        const overlayIndex = overlaysByPage.indexOf(overlay);
        if (overlayIndex === -1) {
            return;
        }
        if (this._renderedPageMap[page]) {
            overlaysByPage[overlayIndex].unmount();
        }
        overlaysByPage.splice(overlayIndex, 1);
        if (overlaysByPage.length === 0) {
            delete this._pages[page];
        }
    }
    updateOverlays(renderedPages) {
        const previouslyRendered = this._renderedPages;
        const newRenderedMap = {};
        renderedPages.map((pageIndex)=>{
            newRenderedMap[pageIndex] = true;
            if (!this._renderedPageMap[pageIndex]) {
                this._renderedPageMap[pageIndex] = true;
                this._invokeOnOverlays(pageIndex, (overlay)=>{
                    overlay.mount();
                });
            }
        });
        previouslyRendered.map((pageIndex)=>{
            if (newRenderedMap[pageIndex]) {
                this._invokeOnOverlays(pageIndex, (overlay)=>{
                    overlay.refresh();
                });
            } else {
                delete this._renderedPageMap[pageIndex];
                this._invokeOnOverlays(pageIndex, (overlay)=>{
                    overlay.unmount();
                });
            }
        });
        this._renderedPages = renderedPages;
    }
    _invokeOnOverlays(pageIndex, func) {
        const overlays = this._pages[pageIndex];
        if (overlays) {
            overlays.map((o)=>func(o));
        }
    }
    constructor(){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_pages", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_renderedPages", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_renderedPageMap", void 0);
        this._pages = {};
        this._renderedPages = [];
        this._renderedPageMap = {};
    }
}



}),
"./source/js/page-tools-overlay.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (PageToolsOverlay)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _utils_elt__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/elt.ts");


class PageToolsOverlay {
    mount() {
        if (this._pageToolsElem === null) {
            this._buttons = this._initializePageToolButtons();
            this._pageToolsElem = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'diva-page-tools-wrapper'
            }, (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'diva-page-tools'
            }, this._buttons));
            this._pageLabelsElem = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'diva-page-labels-wrapper'
            }, (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'diva-page-labels'
            }, this._viewerCore.settings.manifest.pages[this.page].l));
        }
        this.refresh();
        this._innerElement.appendChild(this._pageToolsElem);
        this._innerElement.appendChild(this._pageLabelsElem);
    }
    _initializePageToolButtons() {
        // Callback parameters
        const settings = this._viewerCore.getSettings();
        const publicInstance = this._viewerCore.getPublicInstance();
        const pageIndex = this.page;
        return this._viewerCore.getPageTools().map((plugin)=>{
            // !!! The node needs to be cloned otherwise it is detached from
            //  one and reattached to the other.
            const button = plugin.pageToolsIcon.cloneNode(true);
            // ensure the plugin instance is handed as the first argument to call;
            // this will set the context (i.e., `this`) of the handleClick call to the plugin instance
            // itself.
            button.addEventListener('click', (event)=>{
                plugin.handleClick.call(plugin, event, settings, publicInstance, pageIndex);
            }, false);
            button.addEventListener('touchend', (event)=>{
                // Prevent firing of emulated mouse events
                event.preventDefault();
                plugin.handleClick.call(plugin, event, settings, publicInstance, pageIndex);
            }, false);
            return button;
        });
    }
    unmount() {
        this._innerElement.removeChild(this._pageToolsElem);
        this._innerElement.removeChild(this._pageLabelsElem);
    }
    refresh() {
        const pos = this._viewerCore.getPageRegion(this.page, {
            includePadding: true,
            incorporateViewport: true
        });
        // if window is resized larger, a margin is created - need to subtract this from offsets
        let marginLeft = window.getComputedStyle(this._innerElement, null).getPropertyValue('margin-left');
        this._pageToolsElem.style.top = `${pos.top}px`;
        this._pageToolsElem.style.left = `${pos.left - parseInt(marginLeft)}px`;
        this._pageLabelsElem.style.top = `${pos.top}px`;
        this._pageLabelsElem.style.left = `${pos.right - parseInt(marginLeft) - this.labelWidth - 5}px`;
    }
    constructor(pageIndex, viewerCore){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "page", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_viewerCore", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_innerElement", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_pageToolsElem", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_pageLabelsElem", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "labelWidth", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_1__._)(this, "_buttons", void 0);
        this.page = pageIndex;
        this._viewerCore = viewerCore;
        this._innerElement = this._viewerCore.getSettings().innerElement;
        this._pageToolsElem = null;
        this.labelWidth = 0;
    }
}
/**
*
*
**/ 


}),
"./source/js/parse-iiif-manifest.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (parseIIIFManifest)
});
/* ESM import */var _utils_parse_label_value__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/parse-label-value.ts");

const getMaxZoomLevel = (width, height)=>{
    const largestDimension = Math.max(width, height);
    if (largestDimension < 128) {
        return 0;
    }
    return Math.ceil(Math.log((largestDimension + 1) / (256 + 1)) / Math.log(2));
};
const incorporateZoom = (imageDimension, zoomDifference)=>imageDimension / Math.pow(2, zoomDifference);
const getOtherImageData = (otherImages, lowestMaxZoom)=>{
    return otherImages.map((itm)=>{
        const w = itm.width;
        const h = itm.height;
        const info = parseImageInfo(itm);
        const url = info.url.slice(-1) !== '/' ? info.url + '/' : info.url; // append trailing slash to url if it's not there.
        const dims = new Array(lowestMaxZoom + 1);
        for(let j = 0; j < lowestMaxZoom + 1; j++){
            dims[j] = {
                h: Math.floor(incorporateZoom(h, lowestMaxZoom - j)),
                w: Math.floor(incorporateZoom(w, lowestMaxZoom - j))
            };
        }
        return {
            f: info.url,
            url: url,
            il: itm.label || "",
            d: dims
        };
    });
};
const getIIIFPresentationVersion = (context)=>{
    if (context === "http://iiif.io/api/presentation/2/context.json") {
        return 2;
    } else if (Array.isArray(context) && context.includes("http://iiif.io/api/presentation/2/context.json")) {
        return 2;
    } else if (Array.isArray(context) && context.includes("http://iiif.io/api/presentation/3/context.json")) {
        return 3;
    } else {
        return 2; // Assume a v2 manifest.
    }
};
/**
 * Parses an IIIF Presentation API Manifest and converts it into a Diva.js-format object
 * (See https://github.com/DDMAL/diva.js/wiki/Development-notes#data-received-through-ajax-request)
 *
 * @param {Object} manifest - an object that represents a valid IIIF manifest
 * @returns {Object} divaServiceBlock - the data needed by Diva to show a view of a single document
 */ function parseIIIFManifest(manifest) {
    let ctx = manifest["@context"] || null;
    if (!ctx) {
        console.error("Invalid IIIF Manifest; No @context found.");
        return null;
    }
    const version = getIIIFPresentationVersion(ctx);
    const sequence = manifest.sequences ? manifest.sequences[0] : null;
    const canvases = sequence ? sequence.canvases : manifest.items;
    const numCanvases = canvases.length;
    const pages = new Array(canvases.length);
    let thisCanvas, thisResource, thisImage, secondaryImages, otherImages = [], context, url, info, imageAPIVersion, width, height, maxZoom, canvas, label, imageLabel, zoomDimensions, widthAtCurrentZoomLevel, heightAtCurrentZoomLevel;
    let lowestMaxZoom = 100;
    let maxRatio = 0;
    let minRatio = 100;
    // quickly determine the lowest possible max zoom level (i.e., the upper bound for images) across all canvases.
    // while we're here, compute the global ratios as well.
    for(let z = 0; z < numCanvases; z++){
        const c = canvases[z]; // canvas
        const w = c.width; // canvas width
        const h = c.height; // canvas height
        const mz = getMaxZoomLevel(w, h); // max zoom level
        const ratio = h / w;
        maxRatio = Math.max(ratio, maxRatio);
        minRatio = Math.min(ratio, minRatio);
        lowestMaxZoom = Math.min(lowestMaxZoom, mz);
    }
    /*
        These arrays need to be pre-initialized since we will do arithmetic and value checking on them
    */ const totalWidths = new Array(lowestMaxZoom + 1).fill(0);
    const totalHeights = new Array(lowestMaxZoom + 1).fill(0);
    const maxWidths = new Array(lowestMaxZoom + 1).fill(0);
    const maxHeights = new Array(lowestMaxZoom + 1).fill(0);
    for(let i = 0; i < numCanvases; i++){
        thisCanvas = canvases[i];
        canvas = thisCanvas['@id'] || thisCanvas.id;
        label = thisCanvas.label;
        thisResource = thisCanvas.images ? thisCanvas.images[0].resource : thisCanvas.items[0].items[0].body;
        /*
         * If a canvas has multiple images it will be encoded
         * with a resource type of "oa:Choice" (v2) or "Choice" (v3).
         **/ otherImages = []; // reset array
        if (thisResource['@type'] === "oa:Choice" || thisResource.type === "Choice") {
            thisImage = thisResource.default || thisResource.items[0];
            secondaryImages = thisResource.item || thisResource.items.slice(1);
            otherImages = getOtherImageData(secondaryImages, lowestMaxZoom);
        } else {
            thisImage = thisResource;
        }
        // Prioritize the canvas height / width first, since images may not have h/w
        width = thisCanvas.width || thisImage.width;
        height = thisCanvas.height || thisImage.height;
        if (width <= 0 || height <= 0) {
            console.warn('Invalid width or height for canvas ' + label + '. Skipping');
            continue;
        }
        maxZoom = getMaxZoomLevel(width, height);
        imageLabel = thisImage.label || null;
        info = parseImageInfo(thisImage);
        url = info.url.slice(-1) !== '/' ? info.url + '/' : info.url; // append trailing slash to url if it's not there.
        context = thisImage.service['@context'] || thisImage.service.type;
        if (context === 'http://iiif.io/api/image/2/context.json' || context === "ImageService2") {
            imageAPIVersion = 2;
        } else if (context === 'http://library.stanford.edu/iiif/image-api/1.1/context.json') {
            imageAPIVersion = 1.1;
        } else {
            imageAPIVersion = 1.0;
        }
        zoomDimensions = new Array(lowestMaxZoom + 1);
        for(let k = 0; k < lowestMaxZoom + 1; k++){
            widthAtCurrentZoomLevel = Math.floor(incorporateZoom(width, lowestMaxZoom - k));
            heightAtCurrentZoomLevel = Math.floor(incorporateZoom(height, lowestMaxZoom - k));
            zoomDimensions[k] = {
                h: heightAtCurrentZoomLevel,
                w: widthAtCurrentZoomLevel
            };
            totalWidths[k] += widthAtCurrentZoomLevel;
            totalHeights[k] += heightAtCurrentZoomLevel;
            maxWidths[k] = Math.max(widthAtCurrentZoomLevel, maxWidths[k]);
            maxHeights[k] = Math.max(heightAtCurrentZoomLevel, maxHeights[k]);
        }
        let isPaged = thisCanvas.viewingHint !== 'non-paged' || (thisCanvas.behavior ? thisCanvas.behavior[0] !== 'non-paged' : false);
        let isFacing = thisCanvas.viewingHint === 'facing-pages' || (thisCanvas.behavior ? thisCanvas.behavior[0] === 'facing-pages' : false);
        pages[i] = {
            d: zoomDimensions,
            m: maxZoom,
            l: label,
            il: imageLabel,
            f: info.url,
            url: url,
            api: imageAPIVersion,
            paged: isPaged,
            facingPages: isFacing,
            canvas: canvas,
            otherImages: otherImages,
            xoffset: info.x || null,
            yoffset: info.y || null
        };
    }
    const averageWidths = new Array(lowestMaxZoom + 1).fill(0);
    const averageHeights = new Array(lowestMaxZoom + 1).fill(0);
    for(let a = 0; a < lowestMaxZoom + 1; a++){
        averageWidths[a] = totalWidths[a] / numCanvases;
        averageHeights[a] = totalHeights[a] / numCanvases;
    }
    const dims = {
        a_wid: averageWidths,
        a_hei: averageHeights,
        max_w: maxWidths,
        max_h: maxHeights,
        max_ratio: maxRatio,
        min_ratio: minRatio,
        t_hei: totalHeights,
        t_wid: totalWidths
    };
    // assumes paged is false for non-paged values
    return {
        version: version,
        item_title: (0,_utils_parse_label_value__WEBPACK_IMPORTED_MODULE_0__["default"])(manifest).label,
        metadata: manifest.metadata || null,
        dims: dims,
        max_zoom: lowestMaxZoom,
        pgs: pages,
        paged: manifest.viewingHint === 'paged' || (manifest.behaviour ? manifest.behaviour[0] === 'paged' : false) || (sequence ? sequence.viewingHint === 'paged' : false)
    };
}
/**
 * Takes in a resource block from a canvas and outputs the following information associated with that resource:
 * - Image URL
 * - Image region to be displayed
 *
 * @param {Object} resource - an object representing the resource block of a canvas section in a IIIF manifest
 * @returns {Object} imageInfo - an object containing image URL and region
 */ function parseImageInfo(resource) {
    let url = resource['@id'] || resource.id;
    const fragmentRegex = /#xywh=([0-9]+,[0-9]+,[0-9]+,[0-9]+)/;
    let xywh = '';
    let stripURL = true;
    if (/\/([0-9]+,[0-9]+,[0-9]+,[0-9]+)\//.test(url)) {
        // if resource in image API format, extract region x,y,w,h from URL (after 4th slash from last)
        // matches coordinates in URLs of the form http://www.example.org/iiif/book1-page1/40,50,1200,1800/full/0/default.jpg
        const urlArray = url.split('/');
        xywh = urlArray[urlArray.length - 4];
    } else if (fragmentRegex.test(url)) {
        // matches coordinates of the style http://www.example.org/iiif/book1/canvas/p1#xywh=50,50,320,240
        const result = fragmentRegex.exec(url);
        xywh = result[1];
    } else if (resource.service && (resource.service['@id'] || resource.service.id)) {
        // this URL excludes region parameters so we don't need to remove them
        url = resource.service['@id'] || resource.service.id;
        stripURL = false;
    }
    if (stripURL) {
        // extract URL up to identifier (we eliminate the last 5 parameters: /region/size/rotation/quality.format)
        url = url.split('/').slice(0, -4).join('/');
    }
    const imageInfo = {
        url: url
    };
    if (xywh.length) {
        // parse into separate components
        const dimensions = xywh.split(',');
        imageInfo.x = parseInt(dimensions[0], 10);
        imageInfo.y = parseInt(dimensions[1], 10);
        imageInfo.w = parseInt(dimensions[2], 10);
        imageInfo.h = parseInt(dimensions[3], 10);
    }
    return imageInfo;
}


}),
"./source/js/renderer.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (Renderer)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _utils_elt__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/elt.ts");
/* ESM import */var _composite_image__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./source/js/composite-image.ts");
/* ESM import */var _document_layout__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__("./source/js/document-layout.ts");
/* ESM import */var _image_cache__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__("./source/js/image-cache.ts");
/* ESM import */var _image_request_handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__("./source/js/image-request-handler.ts");
/* ESM import */var _interpolate_animation__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__("./source/js/interpolate-animation.ts");







const REQUEST_DEBOUNCE_INTERVAL = 250;
class Renderer {
    static getCompatibilityErrors() {
        if (typeof HTMLCanvasElement !== 'undefined') {
            return null;
        }
        return [
            'Your browser lacks support for the canvas element. Please upgrade your browser.'
        ];
    }
    load(config, viewportPosition, sourceResolver) {
        this._clearAnimation();
        if (this._hooks.onViewWillLoad) {
            this._hooks.onViewWillLoad();
        }
        this._sourceResolver = sourceResolver;
        this._config = config;
        this._compositeImages = {};
        this._setLayoutToZoomLevel(viewportPosition.zoomLevel);
        // FIXME(wabain): Remove this when there's more confidence the check shouldn't be needed
        if (this.layout && !this.layout.getPageInfo(viewportPosition.anchorPage)) {
            //throw new Error('invalid page: ' + viewportPosition.anchorPage);
            viewportPosition.anchorPage = parseInt(this.layout.getIndexOfFirstPage(), 10);
        }
        if (this._canvas.width !== this._viewport.width || this._canvas.height !== this._viewport.height) {
            this._canvas.width = this._viewport.width;
            this._canvas.height = this._viewport.height;
        }
        // FIXME: What hooks should be called here?
        this.goto(viewportPosition.anchorPage, viewportPosition.verticalOffset, viewportPosition.horizontalOffset);
        if (this._canvas.parentNode !== this._outerElement) {
            this._outerElement.insertBefore(this._canvas, this._outerElement.firstChild);
        }
        if (this._hooks.onViewDidLoad) {
            this._hooks.onViewDidLoad();
        }
    }
    _setViewportPosition(viewportPosition) {
        if (viewportPosition.zoomLevel !== this._zoomLevel) {
            if (this._zoomLevel === null) {
                throw new TypeError('The current view is not zoomable');
            } else if (viewportPosition.zoomLevel === null) {
                throw new TypeError('The current view requires a zoom level');
            }
            this._setLayoutToZoomLevel(viewportPosition.zoomLevel);
        }
        this._goto(viewportPosition.anchorPage, viewportPosition.verticalOffset, viewportPosition.horizontalOffset);
    }
    _setLayoutToZoomLevel(zoomLevel) {
        this.layout = new _document_layout__WEBPACK_IMPORTED_MODULE_2__["default"](this._config, zoomLevel);
        this._zoomLevel = zoomLevel;
        (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.setAttributes)(this._documentElement, {
            style: {
                height: this.layout.dimensions.height + 'px',
                width: this.layout.dimensions.width + 'px'
            }
        });
        this._viewport.setInnerDimensions(this.layout.dimensions);
    }
    adjust() {
        this._clearAnimation();
        this._render();
        if (this._hooks.onViewDidUpdate) {
            this._hooks.onViewDidUpdate(this._renderedPages.slice(), null);
        }
    }
    _render() {
        const newRenderedPages = [];
        this.layout.pageGroups.forEach((group)=>{
            if (!this._viewport.intersectsRegion(group.region)) {
                return;
            }
            const visiblePages = group.pages.filter((page)=>{
                return this.isPageVisible(page.index);
            }).map((page)=>page.index);
            newRenderedPages.push.apply(newRenderedPages, visiblePages);
        }, this);
        this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height);
        this._paintOutline(newRenderedPages);
        newRenderedPages.forEach((pageIndex)=>{
            if (!this._compositeImages[pageIndex]) {
                const page = this.layout.getPageInfo(pageIndex);
                const zoomLevels = this._sourceResolver.getAllZoomLevelsForPage(page);
                const composite = new _composite_image__WEBPACK_IMPORTED_MODULE_1__["default"](zoomLevels);
                composite.updateFromCache(this._cache);
                this._compositeImages[pageIndex] = composite;
            }
        });
        this._initiateTileRequests(newRenderedPages);
        const changes = findChanges(this._renderedPages || [], newRenderedPages);
        changes.removed.forEach((pageIndex)=>{
            delete this._compositeImages[pageIndex];
        });
        this._renderedPages = newRenderedPages;
        this._paint();
        if (this._hooks.onPageWillLoad) {
            changes.added.forEach((pageIndex)=>{
                this._hooks.onPageWillLoad(pageIndex);
            }, this);
        }
    }
    _paint() {
        const renderedTiles = [];
        this._renderedPages.forEach((pageIndex)=>{
            this._compositeImages[pageIndex].getTiles(this._zoomLevel).forEach((source)=>{
                const scaled = getScaledTileRecord(source, this._zoomLevel);
                if (this._isTileVisible(pageIndex, scaled)) {
                    renderedTiles.push(source.url);
                    this._drawTile(pageIndex, scaled, this._cache.get(source.url));
                }
            });
        });
        const cache = this._cache;
        const changes = findChanges(this._renderedTiles || [], renderedTiles);
        changes.added.forEach((url)=>{
            cache.acquire(url);
        });
        changes.removed.forEach((url)=>{
            cache.release(url);
        });
        if (changes.removed) {
            // FIXME: Should only need to update the composite images
            // for which tiles were removed
            this._renderedPages.forEach((pageIndex)=>{
                this._compositeImages[pageIndex].updateFromCache(this._cache);
            }, this);
        }
        this._renderedTiles = renderedTiles;
    }
    // Paint a page outline while the tiles are loading.
    _paintOutline(pages) {
        pages.forEach((pageIndex)=>{
            let pageInfo = this.layout.getPageInfo(pageIndex);
            let pageOffset = this._getImageOffset(pageIndex);
            // Ensure the document is drawn to the center of the viewport
            let viewportPaddingX = Math.max(0, (this._viewport.width - this.layout.dimensions.width) / 2);
            let viewportPaddingY = Math.max(0, (this._viewport.height - this.layout.dimensions.height) / 2);
            let viewportOffsetX = pageOffset.left - this._viewport.left + viewportPaddingX;
            let viewportOffsetY = pageOffset.top - this._viewport.top + viewportPaddingY;
            let destXOffset = viewportOffsetX < 0 ? -viewportOffsetX : 0;
            let destYOffset = viewportOffsetY < 0 ? -viewportOffsetY : 0;
            let canvasX = Math.max(0, viewportOffsetX);
            let canvasY = Math.max(0, viewportOffsetY);
            let destWidth = pageInfo.dimensions.width - destXOffset;
            let destHeight = pageInfo.dimensions.height - destYOffset;
            this._ctx.strokeStyle = '#AAA';
            // In order to get a 1px wide line using strokes, we need to start at a 'half pixel'
            this._ctx.strokeRect(canvasX + 0.5, canvasY + 0.5, destWidth, destHeight);
        });
    }
    // This method should be sent all visible pages at once because it will initiate
    // all image requests and cancel any remaining image requests. In the case that
    // a request is ongoing and the tile is still visible in the viewport, the old request
    // is kept active instead of restarting it. The image requests are given a timeout
    // before loading in order to debounce them and have a small reaction time
    // to cancel them and avoid useless requests.
    _initiateTileRequests(pages) {
        // Only requests in this object are kept alive, since all others are not visible in the viewport
        const newPendingRequests = {};
        // Used later as a closure to initiate the image requests with the right source and pageIndex
        const initiateRequest = (source, pageIndex)=>{
            const composite = this._compositeImages[pageIndex];
            newPendingRequests[source.url] = new _image_request_handler__WEBPACK_IMPORTED_MODULE_4__["default"]({
                url: source.url,
                timeoutTime: REQUEST_DEBOUNCE_INTERVAL,
                settings: this._settings,
                load: (img)=>{
                    delete this._pendingRequests[source.url];
                    this._cache.put(source.url, img);
                    // Awkward way to check for updates
                    if (composite === this._compositeImages[pageIndex]) {
                        composite.updateWithLoadedUrls([
                            source.url
                        ]);
                        if (this._isTileForSourceVisible(pageIndex, source)) {
                            this._paint();
                        }
                    } else {
                        if (this._isTileForSourceVisible(pageIndex, source)) {
                            this._paint();
                        }
                    }
                },
                error: ()=>{
                    // TODO: Could make a limited number of retries, etc.
                    delete this._pendingRequests[source.url];
                }
            });
        };
        for(let i = 0; i < pages.length; i++){
            const pageIndex = pages[i];
            const tiles = this._sourceResolver.getBestZoomLevelForPage(this.layout.getPageInfo(pageIndex)).tiles;
            for(let j = 0; j < tiles.length; j++){
                const source = tiles[j];
                if (this._cache.has(source.url) || !this._isTileForSourceVisible(pageIndex, source)) {
                    continue;
                }
                // Don't create a new request if the tile is already being loaded
                if (this._pendingRequests[source.url]) {
                    newPendingRequests[source.url] = this._pendingRequests[source.url];
                    delete this._pendingRequests[source.url];
                    continue;
                }
                // Use a closure since the load and error methods are going to be called later and
                // we need to keep the right reference to the source and the page index
                initiateRequest(source, pageIndex);
            }
        }
        for(const url in this._pendingRequests){
            this._pendingRequests[url].abort();
        }
        this._pendingRequests = newPendingRequests;
    }
    _drawTile(pageIndex, scaledTile, img) {
        let tileOffset = this._getTileToDocumentOffset(pageIndex, scaledTile);
        // Ensure the document is drawn to the center of the viewport
        let viewportPaddingX = Math.max(0, (this._viewport.width - this.layout.dimensions.width) / 2);
        let viewportPaddingY = Math.max(0, (this._viewport.height - this.layout.dimensions.height) / 2);
        let viewportOffsetX = tileOffset.left - this._viewport.left + viewportPaddingX;
        let viewportOffsetY = tileOffset.top - this._viewport.top + viewportPaddingY;
        let destXOffset = viewportOffsetX < 0 ? -viewportOffsetX : 0;
        let destYOffset = viewportOffsetY < 0 ? -viewportOffsetY : 0;
        let canvasX = Math.max(0, viewportOffsetX);
        let canvasY = Math.max(0, viewportOffsetY);
        let sourceXOffset = destXOffset / scaledTile.scaleRatio;
        let sourceYOffset = destYOffset / scaledTile.scaleRatio;
        // Ensure that the specified dimensions are no greater than the actual
        // size of the image. Safari won't display the tile if they are.
        let destImgWidth = Math.min(scaledTile.dimensions.width, img.width * scaledTile.scaleRatio) - destXOffset;
        let destImgHeight = Math.min(scaledTile.dimensions.height, img.height * scaledTile.scaleRatio) - destYOffset;
        let destWidth = Math.max(1, Math.round(destImgWidth));
        let destHeight = Math.max(1, Math.round(destImgHeight));
        let sourceWidth = destWidth / scaledTile.scaleRatio;
        let sourceHeight = destHeight / scaledTile.scaleRatio;
        this._ctx.drawImage(img, sourceXOffset, sourceYOffset, sourceWidth, sourceHeight, canvasX, canvasY, destWidth, destHeight);
    }
    _isTileForSourceVisible(pageIndex, tileSource) {
        return this._isTileVisible(pageIndex, getScaledTileRecord(tileSource, this._zoomLevel));
    }
    _isTileVisible(pageIndex, scaledTile) {
        const tileOffset = this._getTileToDocumentOffset(pageIndex, scaledTile);
        // FIXME(wabain): This check is insufficient during a zoom transition
        return this._viewport.intersectsRegion({
            top: tileOffset.top,
            bottom: tileOffset.top + scaledTile.dimensions.height,
            left: tileOffset.left,
            right: tileOffset.left + scaledTile.dimensions.width
        });
    }
    _getTileToDocumentOffset(pageIndex, scaledTile) {
        const imageOffset = this._getImageOffset(pageIndex);
        return {
            top: imageOffset.top + scaledTile.offset.top,
            left: imageOffset.left + scaledTile.offset.left
        };
    }
    _getImageOffset(pageIndex) {
        return this.layout.getPageOffset(pageIndex, {
            includePadding: true
        });
    }
    // TODO: Update signature
    goto(pageIndex, verticalOffset, horizontalOffset) {
        this._clearAnimation();
        this._goto(pageIndex, verticalOffset, horizontalOffset);
        if (this._hooks.onViewDidUpdate) {
            this._hooks.onViewDidUpdate(this._renderedPages.slice(), pageIndex);
        }
    }
    _goto(pageIndex, verticalOffset, horizontalOffset) {
        // FIXME(wabain): Move this logic to the viewer
        const pageOffset = this.layout.getPageOffset(pageIndex);
        const desiredVerticalCenter = pageOffset.top + verticalOffset;
        const top = desiredVerticalCenter - Math.round(this._viewport.height / 2);
        const desiredHorizontalCenter = pageOffset.left + horizontalOffset;
        const left = desiredHorizontalCenter - Math.round(this._viewport.width / 2);
        this._viewport.top = top;
        this._viewport.left = left;
        this._render();
    }
    transitionViewportPosition(options) {
        this._clearAnimation();
        const getPosition = options.getPosition;
        const onViewDidTransition = this._hooks.onViewDidTransition;
        this._animation = _interpolate_animation__WEBPACK_IMPORTED_MODULE_5__["default"].animate({
            duration: options.duration,
            parameters: options.parameters,
            onUpdate: (values)=>{
                this._setViewportPosition(getPosition(values));
                this._hooks.onZoomLevelWillChange(values.zoomLevel);
                if (onViewDidTransition) {
                    onViewDidTransition();
                }
            },
            onEnd: (info)=>{
                if (options.onEnd) {
                    options.onEnd(info);
                }
                if (this._hooks.onViewDidUpdate && !info.interrupted) {
                    this._hooks.onViewDidUpdate(this._renderedPages.slice(), null);
                }
            }
        });
    }
    _clearAnimation() {
        if (this._animation) {
            this._animation.cancel();
            this._animation = null;
        }
    }
    isPageVisible(pageIndex) {
        if (!this.layout) {
            return false;
        }
        const page = this.layout.getPageInfo(pageIndex);
        if (!page) {
            return false;
        }
        return this._viewport.intersectsRegion(this.layout.getPageRegion(pageIndex));
    }
    getRenderedPages() {
        return this._renderedPages.slice();
    }
    destroy() {
        this._clearAnimation();
        // FIXME(wabain): I don't know if we should actually do this
        Object.keys(this._pendingRequests).forEach((req)=>{
            const handler = this._pendingRequests[req];
            delete this._pendingRequests[req];
            handler.abort();
        }, this);
        this._canvas.parentNode.removeChild(this._canvas);
    }
    constructor(options, hooks){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_viewport", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_outerElement", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_documentElement", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_settings", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_hooks", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_canvas", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_ctx", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_sourceResolver", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_renderedPages", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_config", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_zoomLevel", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_compositeImages", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_renderedTiles", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_animation", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_cache", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "_pendingRequests", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_6__._)(this, "layout", void 0);
        this._viewport = options.viewport;
        this._outerElement = options.outerElement;
        this._documentElement = options.innerElement;
        this._settings = options.settings;
        this._hooks = hooks || {};
        this._canvas = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('canvas', {
            class: 'diva-viewer-canvas'
        });
        this._ctx = this._canvas.getContext('2d');
        // @ts-ignore
        this._ctx.imageSmoothingEnabled = true;
        this.layout = null;
        this._sourceResolver = null;
        this._renderedPages = null;
        this._config = null;
        this._zoomLevel = null;
        this._compositeImages = null;
        this._renderedTiles = null;
        this._animation = null;
        // FIXME(wabain): What level should this be maintained at?
        // Diva global?
        this._cache = new _image_cache__WEBPACK_IMPORTED_MODULE_3__["default"]();
        this._pendingRequests = {};
    }
}

function getScaledTileRecord(source, scaleFactor) {
    let scaleRatio;
    if (scaleFactor === null) {
        scaleRatio = 1;
    } else {
        scaleRatio = Math.pow(2, scaleFactor - source.zoomLevel);
    }
    return {
        sourceZoomLevel: source.zoomLevel,
        scaleRatio: scaleRatio,
        row: source.row,
        col: source.col,
        dimensions: {
            width: source.dimensions.width * scaleRatio,
            height: source.dimensions.height * scaleRatio
        },
        offset: {
            left: source.offset.left * scaleRatio,
            top: source.offset.top * scaleRatio
        },
        url: source.url
    };
}
function findChanges(oldArray, newArray) {
    if (oldArray === newArray) {
        return {
            added: [],
            removed: []
        };
    }
    const removed = oldArray.filter((oldEntry)=>newArray.indexOf(oldEntry) === -1);
    const added = newArray.filter((newEntry)=>oldArray.indexOf(newEntry) === -1);
    return {
        added: added,
        removed: removed
    };
}


}),
"./source/js/tile-coverage-map.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (TileCoverageMap)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");

class TileCoverageMap {
    isLoaded(row, col) {
        // Return true for out of bounds tiles because they
        // don't need to load. (Unfortunately this will also
        // mask logical errors.)
        if (row >= this._rows || col >= this._cols) {
            return true;
        }
        return this._map[row][col];
    }
    set(row, col, value) {
        this._map[row][col] = value;
    }
    constructor(rows, cols){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_rows", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_cols", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_map", void 0);
        this._rows = rows;
        this._cols = cols;
        this._map = new Array(rows).fill(null).map(()=>new Array(cols).fill(false));
    }
}



}),
"./source/js/toolbar.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (Toolbar)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _diva_global__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/diva-global.ts");
/* ESM import */var _utils_elt__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./source/js/utils/elt.ts");



class Toolbar {
    _elemAttrs(ident, base) {
        const attrs = {
            id: this.settings.ID + ident,
            class: 'diva-' + ident
        };
        if (base) {
            return Object.assign(attrs, base);
        } else {
            return attrs;
        }
    }
    /** Convenience function to subscribe to a Diva event */ _subscribe(event, callback) {
        _diva_global__WEBPACK_IMPORTED_MODULE_0__["default"].Events.subscribe(event, callback, this.settings.ID);
    }
    createButton(name, label, callback, icon) {
        const button = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('button', {
            type: 'button',
            id: this.settings.ID + name,
            class: 'diva-' + name + ' diva-button',
            title: label,
            'aria-label': label
        });
        if (icon) {
            button.appendChild(icon);
        }
        if (callback) {
            button.addEventListener('click', callback);
        }
        return button;
    }
    createLabel(name, id, label, innerName, innerValue) {
        return (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', {
            id: this.settings.ID + id,
            class: name + ' diva-label'
        }, [
            label,
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('span', {
                id: this.settings.ID + innerName
            }, innerValue)
        ]);
    }
    createZoomButtons() {
        let zoomOutIcon = this._createZoomOutIcon();
        let zoomInIcon = this._createZoomInIcon();
        let zoomButtons = [
            this.createButton('zoom-out-button', 'Zoom Out', ()=>{
                this.viewer.setZoomLevel(this.settings.zoomLevel - 1);
            }, zoomOutIcon),
            this.createButton('zoom-in-button', 'Zoom In', ()=>{
                this.viewer.setZoomLevel(this.settings.zoomLevel + 1);
            }, zoomInIcon),
            this.createLabel('diva-zoom-label', 'zoom-label', 'Zoom level: ', 'zoom-level', this.settings.zoomLevel + 1)
        ];
        let zoomHandler = ()=>{
            let labelEl = document.getElementById(this.settings.ID + 'zoom-level');
            labelEl.textContent = this.settings.zoomLevel + 1;
        };
        this._subscribe('ZoomLevelDidChange', zoomHandler);
        this._subscribe('ViewerDidLoad', zoomHandler);
        return (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', {
            id: this.settings.ID + "zoom-controls",
            style: "display: none"
        }, zoomButtons);
    }
    createGridControls() {
        let gridMoreIcon = this._createGridMoreIcon();
        let gridFewerIcon = this._createGridFewerIcon();
        let gridButtons = [
            this.createButton('grid-out-button', 'Fewer', ()=>{
                this.viewer.setGridPagesPerRow(this.settings.pagesPerRow - 1);
            }, gridFewerIcon),
            this.createButton('grid-in-button', 'More', ()=>{
                this.viewer.setGridPagesPerRow(this.settings.pagesPerRow + 1);
            }, gridMoreIcon),
            this.createLabel('diva-grid-label', 'grid-label', 'Pages per row: ', 'pages-per-row', this.settings.pagesPerRow)
        ];
        let gridChangeHandler = ()=>{
            let labelEl = document.getElementById(this.settings.ID + 'pages-per-row');
            labelEl.textContent = this.settings.pagesPerRow;
        };
        this._subscribe('GridRowNumberDidChange', gridChangeHandler);
        return (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', {
            id: this.settings.ID + "grid-controls",
            style: "display:none"
        }, gridButtons);
    }
    createPageLabel() {
        // Current page
        const currentPage = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('span', {
            id: this.settings.ID + 'current-page'
        });
        const updateCurrentPage = ()=>{
            // get labels for index range
            let indices = this.viewer.getCurrentPageIndices();
            let startIndex = indices[0];
            let endIndex = indices[indices.length - 1];
            let startLabel = this.settings.manifest.pages[startIndex].l;
            let endLabel = this.settings.manifest.pages[endIndex].l;
            if (startIndex !== endIndex) {
                if (this.settings.enableIndexAsLabel) {
                    currentPage.textContent = startIndex + " - " + endIndex;
                } else {
                    currentPage.textContent = startLabel + " - " + endLabel;
                }
            } else {
                if (this.settings.enableIndexAsLabel) {
                    currentPage.textContent = startIndex;
                } else {
                    currentPage.textContent = startLabel;
                }
            }
        };
        this._subscribe('VisiblePageDidChange', updateCurrentPage);
        this._subscribe('ViewerDidLoad', updateCurrentPage);
        this._subscribe('ViewDidSwitch', updateCurrentPage);
        return (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('span', {
            class: 'diva-page-label diva-label'
        }, currentPage);
    }
    createGotoPageForm() {
        const gotoPageInput = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('input', {
            id: this.settings.ID + 'goto-page-input',
            class: 'diva-input diva-goto-page-input',
            autocomplete: 'off',
            type: 'text',
            'aria-label': 'Page Input'
        });
        const gotoPageSubmit = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('input', {
            id: this.settings.ID + 'goto-page-submit',
            class: 'diva-button diva-button-text',
            type: 'submit',
            value: 'Go'
        });
        const inputSuggestions = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', {
            id: this.settings.ID + 'input-suggestions',
            class: 'diva-input-suggestions'
        });
        const gotoForm = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('form', {
            id: this.settings.ID + 'goto-page',
            class: 'diva-goto-form'
        }, gotoPageInput, gotoPageSubmit, inputSuggestions);
        gotoForm.addEventListener('submit', (e)=>{
            e.preventDefault();
            const desiredPageLabel = gotoPageInput.value;
            if (this.settings.onGotoSubmit && typeof this.settings.onGotoSubmit === "function") {
                const pageIndex = this.settings.onGotoSubmit(desiredPageLabel);
                if (!this.viewer.gotoPageByIndex(pageIndex)) window.alert("No page could be found with that label or page number");
            } else {
                if (!this.viewer.gotoPageByLabel(desiredPageLabel)) window.alert("No page could be found with that label or page number");
            }
            // Hide the suggestions
            inputSuggestions.style.display = 'none';
            // Prevent the default action of reloading the page
            return false;
        });
        [
            'input',
            'focus'
        ].forEach((event)=>{
            gotoPageInput.addEventListener(event, ()=>{
                inputSuggestions.innerHTML = ''; // Remove all previous suggestions
                const value = gotoPageInput.value;
                let numSuggestions = 0;
                if (this.settings.enableGotoSuggestions && value) {
                    const pages = this.settings.manifest.pages;
                    for(let i = 0, len = pages.length; i < len && numSuggestions < 10; i++){
                        if (pages[i].l.toLowerCase().indexOf(value.toLowerCase()) > -1) {
                            const newInputSuggestion = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', {
                                class: 'diva-input-suggestion'
                            }, pages[i].l);
                            inputSuggestions.appendChild(newInputSuggestion);
                            numSuggestions++;
                        }
                    }
                    // Show label suggestions
                    if (numSuggestions > 0) inputSuggestions.style.display = 'block';
                } else inputSuggestions.style.display = 'none';
            });
        });
        gotoPageInput.addEventListener('keydown', (e)=>{
            let el;
            if (e.code === 'Enter') {
                const active = document.getElementsByClassName('active')[0];
                if (typeof active !== 'undefined') {
                    gotoPageInput.value = active.innerText;
                }
            }
            if (e.code === 'ArrowUp') {
                el = document.getElementsByClassName('active')[0];
                const prevEl = el ? el.previousSibling : undefined;
                if (typeof prevEl !== 'undefined') {
                    el.classList.remove('active');
                    if (prevEl !== null) {
                        prevEl.classList.add('active');
                    }
                } else {
                    let last = document.getElementsByClassName('diva-input-suggestion').length - 1;
                    document.getElementsByClassName('diva-input-suggestion')[last].classList.add('active');
                }
            } else if (e.code === 'ArrowDown') {
                el = document.getElementsByClassName('active')[0];
                const nextEl = el ? el.nextSibling : undefined;
                if (typeof nextEl !== 'undefined') {
                    el.classList.remove('active');
                    if (nextEl !== null) {
                        nextEl.classList.add('active');
                    }
                } else {
                    document.getElementsByClassName('diva-input-suggestion')[0].classList.add('active');
                }
            }
        });
        onEvent(inputSuggestions, 'mousedown', '.diva-input-suggestion', ()=>{
            gotoPageInput.value = this.textContent;
            inputSuggestions.style.display = 'none';
            let submitEvent = new Event('submit', {
                cancelable: true
            });
            gotoForm.dispatchEvent(submitEvent);
        });
        // javascript equivalent to jquery .on(event, selector, function)
        function onEvent(elem, evt, sel, handler) {
            elem.addEventListener(evt, (event)=>{
                let t = event.target;
                while(t && t !== this){
                    if (t.matches(sel)) {
                        handler.call(t, event);
                    }
                    t = t.parentNode;
                }
            });
        }
        gotoPageInput.addEventListener('blur', ()=>{
            // Hide label suggestions
            inputSuggestions.style.display = 'none';
        });
        return gotoForm;
    }
    createViewMenu() {
        const viewOptionsList = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', this._elemAttrs('view-options'));
        const gridViewIcon = this._createGridViewIcon();
        const bookViewIcon = this._createBookViewIcon();
        const pageViewIcon = this._createPageViewIcon();
        const viewOptionsToggle = ()=>{
            viewOptionsList.style.display = viewOptionsList.style.display === "none" ? "block" : "none";
        };
        const changeViewButton = this.createButton('view-icon', 'Change view', viewOptionsToggle);
        const selectView = (view)=>{
            this.viewer.changeView(view);
            //hide view menu
            viewOptionsList.style.display = "none";
        };
        const updateViewMenu = ()=>{
            const viewIconClasses = ' diva-view-icon diva-button';
            // display the icon of the mode we're currently in (?)
            if (this.settings.inGrid) {
                changeViewButton.appendChild(gridViewIcon);
                changeViewButton.className = 'diva-grid-icon' + viewIconClasses;
            } else if (this.settings.inBookLayout) {
                changeViewButton.appendChild(bookViewIcon);
                changeViewButton.className = 'diva-book-icon' + viewIconClasses;
            } else {
                changeViewButton.appendChild(pageViewIcon);
                changeViewButton.className = 'diva-document-icon' + viewIconClasses;
            }
            const viewOptions = document.createDocumentFragment();
            // then display document, book, and grid buttons in that order, excluding the current view
            if (this.settings.inGrid || this.settings.inBookLayout) {
                viewOptions.appendChild(this.createButton('document-icon', 'Document View', selectView.bind(null, 'document'), pageViewIcon));
            }
            if (this.settings.inGrid || !this.settings.inBookLayout) {
                viewOptions.appendChild(this.createButton('book-icon', 'Book View', selectView.bind(null, 'book'), bookViewIcon));
            }
            if (!this.settings.inGrid) {
                viewOptions.appendChild(this.createButton('grid-icon', 'Grid View', selectView.bind(null, 'grid'), gridViewIcon));
            }
            // remove old menu
            while(viewOptionsList.firstChild){
                viewOptionsList.removeChild(viewOptionsList.firstChild);
            }
            // insert new menu
            viewOptionsList.appendChild(viewOptions);
        };
        document.addEventListener('mouseup', (event)=>{
            if (viewOptionsList !== event.target) {
                viewOptionsList.style.display = 'none';
            }
        });
        this._subscribe('ViewDidSwitch', updateViewMenu);
        this._subscribe('ObjectDidLoad', updateViewMenu);
        return (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', this._elemAttrs('view-menu'), changeViewButton, viewOptionsList);
    }
    createFullscreenButton() {
        let fullscreenIcon = this._createFullscreenIcon();
        return this.createButton('fullscreen-icon', 'Toggle fullscreen mode', ()=>{
            this.viewer.toggleFullscreenMode();
        }, fullscreenIcon);
    }
    toggleZoomGridControls() {
        if (!this.settings.inGrid) {
            document.getElementById(this.settings.ID + "zoom-controls").style.display = "block";
            document.getElementById(this.settings.ID + "grid-controls").style.display = "none";
        } else {
            document.getElementById(this.settings.ID + "zoom-controls").style.display = "none";
            document.getElementById(this.settings.ID + "grid-controls").style.display = "block";
        }
    }
    render() {
        this._subscribe("ViewDidSwitch", this.toggleZoomGridControls);
        this._subscribe("ObjectDidLoad", this.toggleZoomGridControls);
        let leftTools = [
            this.createZoomButtons(),
            this.createGridControls()
        ];
        let rightTools = [
            this.createPageLabel(),
            this.createViewMenu()
        ];
        if (this.settings.enableFullscreen) {
            rightTools.push(this.createFullscreenButton());
        }
        if (this.settings.enableGotoPage) {
            rightTools.splice(1, 0, this.createGotoPageForm());
        }
        // assign toolbar plugins to proper side
        let plugins = this.viewer.viewerState.pluginInstances;
        for(let i = 0, len = plugins.length; i < len; i++){
            let plugin = plugins[i];
            if (!plugin.toolbarSide) {
                continue;
            }
            plugin.toolbarIcon = plugin.createIcon();
            if (!plugin.toolbarIcon) {
                continue;
            }
            // add plugin tools after the go-to-page and page-label tools
            if (plugin.toolbarSide === 'right') {
                rightTools.splice(2, 0, plugin.toolbarIcon);
            } else if (plugin.toolbarSide === 'left') {
                leftTools.splice(2, 0, plugin.toolbarIcon);
            }
            plugin.toolbarIcon.addEventListener('click', handlePluginClick.bind(this, plugin));
        }
        function handlePluginClick(plugin) {
            plugin.handleClick(this.viewer);
        }
        const tools = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', this._elemAttrs('tools'), (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', this._elemAttrs('tools-left'), leftTools), (0,_utils_elt__WEBPACK_IMPORTED_MODULE_1__.elt)('div', this._elemAttrs('tools-right'), rightTools));
        this.settings.toolbarParentObject.insertBefore(tools, this.settings.toolbarParentObject.firstChild);
    }
    _createToolbarIcon(paths) {
        let icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        icon.setAttributeNS(null, 'viewBox', "0 0 25 25");
        icon.setAttributeNS(null, 'x', '0px');
        icon.setAttributeNS(null, 'y', '0px');
        icon.setAttributeNS(null, 'style', "enable-background:new 0 0 48 48;");
        let glyph = document.createElementNS("http://www.w3.org/2000/svg", "g");
        glyph.setAttributeNS(null, "transform", "matrix(1, 0, 0, 1, -12, -12)");
        paths.forEach((path)=>{
            let pEl = document.createElementNS("http://www.w3.org/2000/svg", "path");
            pEl.setAttributeNS(null, "d", path);
            glyph.appendChild(pEl);
        });
        icon.appendChild(glyph);
        return icon;
    }
    _createZoomOutIcon() {
        let paths = [
            "M19.5,23c-0.275,0-0.5-0.225-0.5-0.5v-1c0-0.275,0.225-0.5,0.5-0.5h7c0.275,0,0.5,0.225,0.5,0.5v1c0,0.275-0.225,0.5-0.5,0.5H19.5z",
            "M37.219,34.257l-2.213,2.212c-0.202,0.202-0.534,0.202-0.736,0l-6.098-6.099c-1.537,0.993-3.362,1.577-5.323,1.577c-5.431,0-9.849-4.418-9.849-9.849c0-5.431,4.418-9.849,9.849-9.849c5.431,0,9.849,4.418,9.849,9.849c0,1.961-0.584,3.786-1.576,5.323l6.098,6.098C37.422,33.722,37.422,34.054,37.219,34.257z M29.568,22.099c0-3.706-3.014-6.72-6.72-6.72c-3.706,0-6.72,3.014-6.72,6.72c0,3.706,3.014,6.72,6.72,6.72C26.555,28.818,29.568,25.805,29.568,22.099z"
        ];
        return this._createToolbarIcon(paths);
    }
    _createZoomInIcon() {
        let paths = [
            "M37.469,34.257l-2.213,2.212c-0.202,0.202-0.534,0.202-0.736,0l-6.098-6.099c-1.537,0.993-3.362,1.577-5.323,1.577c-5.431,0-9.849-4.418-9.849-9.849c0-5.431,4.418-9.849,9.849-9.849c5.431,0,9.849,4.418,9.849,9.849c0,1.961-0.584,3.786-1.576,5.323l6.098,6.098C37.672,33.722,37.672,34.054,37.469,34.257z M29.818,22.099c0-3.706-3.014-6.72-6.72-6.72c-3.706,0-6.72,3.014-6.72,6.72c0,3.706,3.014,6.72,6.72,6.72C26.805,28.818,29.818,25.805,29.818,22.099z M26.5,21H24v-2.5c0-0.275-0.225-0.5-0.5-0.5h-1c-0.275,0-0.5,0.225-0.5,0.5V21h-2.5c-0.275,0-0.5,0.225-0.5,0.5v1c0,0.275,0.225,0.5,0.5,0.5H22v2.5c0,0.275,0.225,0.5,0.5,0.5h1c0.275,0,0.5-0.225,0.5-0.5V23h2.5c0.275,0,0.5-0.225,0.5-0.5v-1C27,21.225,26.775,21,26.5,21z"
        ];
        return this._createToolbarIcon(paths);
    }
    _createGridMoreIcon() {
        let paths = [
            "M29.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z"
        ];
        return this._createToolbarIcon(paths);
    }
    _createGridFewerIcon() {
        let paths = [
            "M25.5,35c-0.275,0-0.5-0.225-0.5-0.5v-9c0-0.275,0.225-0.5,0.5-0.5h9c0.275,0,0.5,0.225,0.5,0.5v9c0,0.275-0.225,0.5-0.5,0.5H25.5z M22.5,35c0.275,0,0.5-0.225,0.5-0.5v-9c0-0.275-0.225-0.5-0.5-0.5h-9c-0.275,0-0.5,0.225-0.5,0.5v9c0,0.275,0.225,0.5,0.5,0.5H22.5z M34.5,23c0.275,0,0.5-0.225,0.5-0.5v-9c0-0.275-0.225-0.5-0.5-0.5h-9c-0.275,0-0.5,0.225-0.5,0.5v9c0,0.275,0.225,0.5,0.5,0.5H34.5z M22.5,23c0.275,0,0.5-0.225,0.5-0.5v-9c0-0.275-0.225-0.5-0.5-0.5h-9c-0.275,0-0.5,0.225-0.5,0.5v9c0,0.275,0.225,0.5,0.5,0.5H22.5z"
        ];
        return this._createToolbarIcon(paths);
    }
    _createGridViewIcon() {
        let paths = [
            "M29.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z"
        ];
        return this._createToolbarIcon(paths);
    }
    _createBookViewIcon() {
        let paths = [
            "M35,16.8v-1.323c0,0-2.292-1.328-5.74-1.328c-3.448,0-5.26,1.25-5.26,1.25s-1.813-1.25-5.26-1.25c-3.448,0-5.74,1.328-5.74,1.328V16.8l-1,0.531v0.021v15.687c0,0,4.531-1.578,6.999-1.578c2.468,0,5.001,0.885,5.001,0.885s2.532-0.885,5-0.885c0.306,0,0.643,0.024,1,0.066v4.325l1.531-2.016L33,35.852v-3.72c2,0.43,3,0.906,3,0.906V17.352v-0.021L35,16.8z M23,29.03c-1-0.292-2.584-0.679-3.981-0.679c-2.246,0-3.019,0.404-4.019,0.699V16.634c0,0,1.125-0.699,4.019-0.699c1.694,0,2.981,0.417,3.981,1.126V29.03z M33,29.051c-1-0.295-1.773-0.699-4.02-0.699c-1.396,0-2.981,0.387-3.98,0.679V17.06c1-0.709,2.286-1.126,3.98-1.126c2.895,0,4.02,0.699,4.02,0.699V29.051z"
        ];
        return this._createToolbarIcon(paths);
    }
    _createPageViewIcon() {
        let paths = [
            "M29.425,29h4.47L29,33.934v-4.47C29,29.19,29.151,29,29.425,29z M34,14.563V28h-5.569C28.157,28,28,28.196,28,28.47V34H14.497C14.223,34,14,33.71,14,33.437V14.563C14,14.29,14.223,14,14.497,14h18.9C33.672,14,34,14.29,34,14.563z M25.497,26.497C25.497,26.223,25.275,26,25,26h-7c-0.275,0-0.497,0.223-0.497,0.497v1.006C17.503,27.777,17.725,28,18,28h7c0.275,0,0.497-0.223,0.497-0.497V26.497z M30.497,22.497C30.497,22.223,30.275,22,30,22H18c-0.275,0-0.497,0.223-0.497,0.497v1.006C17.503,23.777,17.725,24,18,24h12c0.275,0,0.497-0.223,0.497-0.497V22.497z M30.497,18.497C30.497,18.223,30.275,18,30,18H18c-0.275,0-0.497,0.223-0.497,0.497v1.006C17.503,19.777,17.725,20,18,20h12c0.275,0,0.497-0.223,0.497-0.497V18.497z"
        ];
        return this._createToolbarIcon(paths);
    }
    _createFullscreenIcon() {
        let paths = [
            "M35,12H13c-0.55,0-1,0.45-1,1v22c0,0.55,0.45,1,1,1h22c0.55,0,1-0.45,1-1V13C36,12.45,35.55,12,35,12z M34,34H14V14h20V34z",
            "M17,21.75v-4.5c0-0.138,0.112-0.25,0.25-0.25h4.5c0.138,0,0.17,0.08,0.073,0.177l-1.616,1.616l1.823,1.823c0.097,0.097,0.097,0.256,0,0.354l-1.061,1.06c-0.097,0.097-0.256,0.097-0.354,0l-1.823-1.823l-1.616,1.616C17.08,21.92,17,21.888,17,21.75z M20.97,25.97c-0.097-0.097-0.256-0.097-0.354,0l-1.823,1.823l-1.616-1.616C17.08,26.08,17,26.112,17,26.25v4.5c0,0.138,0.112,0.25,0.25,0.25h4.5c0.138,0,0.17-0.08,0.073-0.177l-1.616-1.616l1.823-1.823c0.097-0.097,0.097-0.256,0-0.354L20.97,25.97z M30.75,17h-4.5c-0.138,0-0.17,0.08-0.073,0.177l1.616,1.616l-1.823,1.823c-0.097,0.097-0.097,0.256,0,0.354l1.061,1.06c0.097,0.097,0.256,0.097,0.354,0l1.823-1.823l1.616,1.616C30.92,21.92,31,21.888,31,21.75v-4.5C31,17.112,30.888,17,30.75,17z M30.823,26.177l-1.616,1.616l-1.823-1.823c-0.097-0.097-0.256-0.097-0.354,0l-1.061,1.06c-0.097,0.097-0.097,0.256,0,0.354l1.823,1.823l-1.616,1.616C26.08,30.92,26.112,31,26.25,31h4.5c0.138,0,0.25-0.112,0.25-0.25v-4.5C31,26.112,30.92,26.08,30.823,26.177z M26,22.5c0-0.275-0.225-0.5-0.5-0.5h-3c-0.275,0-0.5,0.225-0.5,0.5v3c0,0.275,0.225,0.5,0.5,0.5h3c0.275,0,0.5-0.225,0.5-0.5V22.5z"
        ];
        return this._createToolbarIcon(paths);
    }
    constructor(viewer){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "settings", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_2__._)(this, "viewer", void 0);
        this.viewer = viewer;
        this.settings = viewer.settings;
    }
}



}),
"./source/js/utils/dragscroll.js": (function (__unused_webpack_module, exports) {
/**
 * @fileoverview dragscroll - scroll area by dragging
 * @version 0.0.8
 *
 * @license MIT, see http://github.com/asvd/dragscroll
 * @copyright 2015 asvd <heliosframework@gmail.com>
 */ (function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([
            'exports'
        ], factory);
    } else if (true) {
        factory(exports);
    } else {}
})(this, function(exports1) {
    var _window = window;
    var _document = document;
    var mousemove = 'mousemove';
    var mouseup = 'mouseup';
    var mousedown = 'mousedown';
    var EventListener = 'EventListener';
    var addEventListener = 'add' + EventListener;
    var removeEventListener = 'remove' + EventListener;
    var newScrollX, newScrollY; // jshint ignore:line
    var dragged = [];
    var reset = function(i, el) {
        for(i = 0; i < dragged.length;){
            el = dragged[i++];
            el = el.container || el;
            el[removeEventListener](mousedown, el.md, 0);
            _window[removeEventListener](mouseup, el.mu, 0);
            _window[removeEventListener](mousemove, el.mm, 0);
        }
        // suppress warning about functions in loops.
        /* jshint ignore:start */ // cloning into array since HTMLCollection is updated dynamically
        dragged = [].slice.call(_document.getElementsByClassName('dragscroll'));
        for(i = 0; i < dragged.length;){
            (function(el, lastClientX, lastClientY, pushed, scroller, cont) {
                (cont = el.container || el)[addEventListener](mousedown, cont.md = function(e) {
                    if (!el.hasAttribute('nochilddrag') || _document.elementFromPoint(e.pageX, e.pageY) === cont) {
                        pushed = 1;
                        lastClientX = e.clientX;
                        lastClientY = e.clientY;
                        e.preventDefault();
                    }
                }, 0);
                _window[addEventListener](mouseup, cont.mu = function() {
                    pushed = 0;
                }, 0);
                _window[addEventListener](mousemove, cont.mm = function(e) {
                    if (pushed) {
                        (scroller = el.scroller || el).scrollLeft -= newScrollX = -lastClientX + (lastClientX = e.clientX);
                        scroller.scrollTop -= newScrollY = -lastClientY + (lastClientY = e.clientY);
                        if (el === _document.body) {
                            (scroller = _document.documentElement).scrollLeft -= newScrollX;
                            scroller.scrollTop -= newScrollY;
                        }
                    }
                }, 0);
            })(dragged[i++]);
        }
    /* jshint ignore:end */ };
    if (_document.readyState === 'complete') {
        reset();
    } else {
        _window[addEventListener]('load', reset, 0);
    }
    exports1.reset = reset;
    window.resetDragscroll = reset;
});


}),
"./source/js/utils/elt.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  elt: () => (elt),
  setAttributes: () => (setDOMAttributes)
});

/**
 * Convenience function to create a DOM element, set attributes on it, and
 * append children. All arguments which are not of primitive type, are not
 * arrays, and are not DOM nodes are treated as attribute hashes and are
 * handled as described for setDOMAttributes. Children can either be a DOM
 * node or a primitive value, which is converted to a text node. Arrays are
 * handled recursively. Null and undefined values are ignored.
 *
 * Inspired by the ProseMirror helper of the same name.
 */ function elt(tag) {
    for(var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++){
        args[_key - 1] = arguments[_key];
    }
    const el = document.createElement(tag);
    while(args.length){
        const arg = args.shift();
        handleEltConstructorArg(el, arg);
    }
    return el;
}
function handleEltConstructorArg(el, arg) {
    if (arg == null) {
        return;
    }
    if (typeof arg !== 'object' && typeof arg !== 'function') {
        // Coerce to string
        el.appendChild(document.createTextNode(arg));
    } else if (arg instanceof window.Node) {
        el.appendChild(arg);
    } else if (arg instanceof Array) {
        const childCount = arg.length;
        for(let i = 0; i < childCount; i++){
            handleEltConstructorArg(el, arg[i]);
        }
    } else {
        setDOMAttributes(el, arg);
    }
}
/**
 * Set attributes of a DOM element. The `style` property is special-cased to
 * accept either a string or an object whose own attributes are assigned to
 * el.style.
 */ function setDOMAttributes(el, attributes) {
    for(const prop in attributes){
        if (!attributes.hasOwnProperty(prop)) {
            continue;
        }
        if (prop === 'style') {
            setStyle(el, attributes.style);
        } else {
            el.setAttribute(prop, attributes[prop]);
        }
    }
}
function setStyle(el, style) {
    if (!style) {
        return;
    }
    if (typeof style !== 'object') {
        el.style.cssText = style;
        return;
    }
    for(const cssProp in style){
        if (!style.hasOwnProperty(cssProp)) {
            continue;
        }
        el.style[cssProp] = style[cssProp];
    }
}


}),
"./source/js/utils/events.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  Events: () => (Events)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/**
 * Events. Pub/Sub system for Loosely Coupled logic.
 * Based on Peter Higgins' port from Dojo to jQuery
 * https://github.com/phiggins42/bloody-jquery-plugins/blob/master/pubsub.js
 *
 * Re-adapted to vanilla Javascript
 *
 * @class Events
 */ 
class DivaEvents {
    /**
     * diva.Events.publish
     * e.g.: diva.Events.publish("PageDidLoad", [pageIndex, filename, pageSelector], this);
     *
     * @class Events
     * @method publish
     * @param topic {String}
     * @param args  {Array}
     * @param scope {Object=} Optional - Subscribed functions will be executed with the supplied object as `this`.
     *     It is necessary to supply this argument with the self variable when within a Diva instance.
     *     The scope argument is matched with the instance ID of subscribers to determine whether they
     *         should be executed. (See instanceID argument of subscribe.)
     */ publish(topic, args, scope) {
        if (this._cache[topic]) {
            const thisTopic = this._cache[topic];
            if (typeof thisTopic.global !== 'undefined') {
                const thisTopicGlobal = thisTopic.global;
                const globalCount = thisTopicGlobal.length;
                for(let i = 0; i < globalCount; i++){
                    thisTopicGlobal[i].apply(scope || null, args || []);
                }
            }
            if (scope && typeof scope.getInstanceId !== 'undefined') {
                // get publisher instance ID from scope arg, compare, and execute if match
                const instanceID = scope.getInstanceId();
                if (this._cache[topic][instanceID]) {
                    const thisTopicInstance = this._cache[topic][instanceID];
                    const scopedCount = thisTopicInstance.length;
                    for(let j = 0; j < scopedCount; j++){
                        thisTopicInstance[j].apply(scope, args || []);
                    }
                }
            }
        }
    }
    /**
     * diva.Events.subscribe
     * e.g.: diva.Events.subscribe("PageDidLoad", highlight, settings.ID)
     *
     * @class Events
     * @method subscribe
     * @param {string} topic
     * @param {function} callback
     * @param {string=} instanceID  Optional - String representing the ID of a Diva instance; if provided,
     *                                       callback only fires for events published from that instance.
     * @return Event handler {Array}
     */ subscribe(topic, callback, instanceID) {
        if (!this._cache[topic]) {
            this._cache[topic] = {};
        }
        if (typeof instanceID === 'string') {
            if (!this._cache[topic][instanceID]) {
                this._cache[topic][instanceID] = [];
            }
            this._cache[topic][instanceID].push(callback);
        } else {
            if (!this._cache[topic].global) {
                this._cache[topic].global = [];
            }
            this._cache[topic].global.push(callback);
        }
        return instanceID ? [
            topic,
            callback,
            instanceID
        ] : [
            topic,
            callback
        ];
    }
    /**
     * diva.Events.unsubscribe
     * e.g.: var handle = Events.subscribe("PageDidLoad", highlight);
     *         Events.unsubscribe(handle);
     *
     * @class Events
     * @method unsubscribe
     * @param {array} handle
     * @param {boolean=} completely - Unsubscribe all events for a given topic.
     * @return {boolean} success
     */ unsubscribe(handle, completely) {
        const t = handle[0];
        if (this._cache[t]) {
            let topicArray;
            const instanceID = handle.length === 3 ? handle[2] : 'global';
            topicArray = this._cache[t][instanceID];
            if (!topicArray) {
                return false;
            }
            if (completely) {
                delete this._cache[t][instanceID];
                return topicArray.length > 0;
            }
            let i = topicArray.length;
            while(i--){
                if (topicArray[i] === handle[1]) {
                    this._cache[t][instanceID].splice(i, 1);
                    return true;
                }
            }
        }
        return false;
    }
    /**
     * diva.Events.unsubscribeAll
     * e.g.: diva.Events.unsubscribeAll('global');
     *
     * @class Events
     * @param {string=} instanceID Optional - instance ID to remove subscribers from or 'global' (if omitted,
     *                              subscribers in all scopes removed)
     * @method unsubscribeAll
     */ unsubscribeAll(instanceID) {
        if (instanceID) {
            const topics = Object.keys(this._cache);
            let i = topics.length;
            let topic;
            while(i--){
                topic = topics[i];
                if (typeof this._cache[topic][instanceID] !== 'undefined') {
                    delete this._cache[topic][instanceID];
                }
            }
        } else {
            this._cache = {};
        }
    }
    constructor(){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_cache", void 0);
        this._cache = {};
    }
}
let Events = new DivaEvents();


}),
"./source/js/utils/get-scrollbar-width.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (getScrollbarWidth)
});
// From http://www.alexandre-gomes.com/?p=115, modified slightly
function getScrollbarWidth() {
    let inner = document.createElement('p');
    inner.style.width = '100%';
    inner.style.height = '200px';
    let outer = document.createElement('div');
    outer.style.position = 'absolute';
    outer.style.top = '0px';
    outer.style.left = '0px';
    outer.style.visibility = 'hidden';
    outer.style.width = '200px';
    outer.style.height = '150px';
    outer.style.overflow = 'hidden';
    outer.appendChild(inner);
    document.body.appendChild(outer);
    let w1 = inner.offsetWidth;
    outer.style.overflow = 'scroll';
    let w2 = inner.offsetWidth;
    if (w1 === w2) {
        w2 = outer.clientWidth; // for IE i think
    }
    document.body.removeChild(outer);
    return w1 - w2;
}


}),
"./source/js/utils/hash-params.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (__WEBPACK_DEFAULT_EXPORT__)
});
let HashParams = {
    get: getHashParam,
    update: updateHashParam
};
/* ESM default export */ const __WEBPACK_DEFAULT_EXPORT__ = (HashParams);
// For getting the #key values from the URL. For specifying a page and zoom level
// Look into caching, because we only need to get this during the initial load
// Although for the tests I guess we would need to override caching somehow
function getHashParam(key) {
    const hash = window.location.hash;
    if (hash !== '') {
        // Check if there is something that looks like either &key= or #key=
        let startIndex = hash.indexOf('&' + key + '=') > 0 ? hash.indexOf('&' + key + '=') : hash.indexOf('#' + key + '=');
        // If startIndex is still -1, it means it can't find either
        if (startIndex >= 0) {
            // Add the length of the key plus the & and =
            startIndex += key.length + 2;
            // Either to the next ampersand or to the end of the string
            const endIndex = hash.indexOf('&', startIndex);
            if (endIndex > startIndex) {
                return decodeURIComponent(hash.substring(startIndex, endIndex));
            } else if (endIndex < 0) {
                // This means this hash param is the last one
                return decodeURIComponent(hash.substring(startIndex));
            }
            // If the key doesn't have a value I think
            return '';
        } else {
            // If it can't find the key
            return false;
        }
    } else {
        // If there are no hash params just return false
        return false;
    }
}
function updateHashParam(key, value) {
    // First make sure that we have to do any work at all
    const originalValue = getHashParam(key);
    const hash = window.location.hash;
    if (originalValue !== value) {
        // Is the key already in the URL?
        if (typeof originalValue === 'string') {
            // Already in the URL. Just get rid of the original value
            const startIndex = hash.indexOf('&' + key + '=') > 0 ? hash.indexOf('&' + key + '=') : hash.indexOf('#' + key + '=');
            const endIndex = startIndex + key.length + 2 + originalValue.length;
            // # if it's the first, & otherwise
            const startThing = startIndex === 0 ? '#' : '&';
            window.location.replace(hash.substring(0, startIndex) + startThing + key + '=' + value + hash.substring(endIndex));
        } else {
            // It's not present - add it
            if (hash.length === 0) {
                window.location.replace('#' + key + '=' + value);
            } else {
                // Append it
                window.location.replace(hash + '&' + key + '=' + value);
            }
        }
    }
}


}),
"./source/js/utils/maxby.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  maxBy: () => (maxBy)
});
function getTag(value) {
    if (value == null) {
        return value === undefined ? '[object Undefined]' : '[object Null]';
    }
    return toString.call(value);
}
function isSymbol(value) {
    const type = typeof value;
    return type === 'symbol' || type === 'object' && value != null && getTag(value) === '[object Symbol]';
}
function maxBy(array, iteratee) {
    let result;
    if (array == null) {
        return result;
    }
    let computed;
    for (const value of array){
        const current = iteratee(value);
        if (current != null && (computed === undefined ? current === current && !isSymbol(current) : current > computed)) {
            computed = current;
            result = value;
        }
    }
    return result;
}


}),
"./source/js/utils/parse-label-value.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (parseLabelValue)
});
/**
 * Parses a v3 manifest's label/value pair from an object & array to a string
 *
 * @public
 * @params {string} key - The key from which a label/value pair should be extracted.
 * @returns {object} - The label/value pair as strings.
 * */ function parseLabelValue(key) {
    let l = key.label;
    let label = typeof l === 'object' ? l[Object.keys(l)[0]][0] : l;
    let v = key.value;
    let value;
    if (Array.isArray(v)) {
        value = v.map((e)=>e[Object.keys(e)[0]]);
    } else {
        value = typeof v === 'object' ? v[Object.keys(v)[0]] : v;
    }
    if (Array.isArray(value)) {
        value = value.join(', ');
    }
    return {
        label: label,
        value: value
    };
}


}),
"./source/js/utils/vanilla.kinetic.ts": (function () {
/*
 The MIT License (MIT)
 Copyright (c) <2011> <Dave Taylor http://the-taylors.org>

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is furnished
 to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 Port to vanilla Javascript by Jacek Nowacki http://jacek-nowacki.net/
**/ (function() {
    var _raf = window.requestAnimationFrame;
    var _isTouch = 'ontouchend' in document;
    // this is simple, no "deep" support
    var _extend = function() {
        for(var i = 1; i < arguments.length; i++){
            for(var key in arguments[i]){
                if (arguments[i].hasOwnProperty(key)) {
                    arguments[0][key] = arguments[i][key];
                }
            }
        }
        return arguments[0];
    };
    var VanillaKinetic = function(element, settings) {
        this.settings = _extend({}, VanillaKinetic.DEFAULTS, settings);
        this.el = element;
        this.ACTIVE_CLASS = "kinetic-active";
        this._initElements();
        this.el._VanillaKinetic = this;
        return this;
    };
    VanillaKinetic.DEFAULTS = {
        cursor: 'move',
        decelerate: true,
        triggerHardware: false,
        threshold: 0,
        y: true,
        x: true,
        slowdown: 0.9,
        maxvelocity: 40,
        throttleFPS: 60,
        invert: false,
        movingClass: {
            up: 'kinetic-moving-up',
            down: 'kinetic-moving-down',
            left: 'kinetic-moving-left',
            right: 'kinetic-moving-right'
        },
        deceleratingClass: {
            up: 'kinetic-decelerating-up',
            down: 'kinetic-decelerating-down',
            left: 'kinetic-decelerating-left',
            right: 'kinetic-decelerating-right'
        }
    };
    // Public functions
    VanillaKinetic.prototype.start = function(options) {
        this.settings = _extend(this.settings, options);
        this.velocity = options.velocity || this.velocity;
        this.velocityY = options.velocityY || this.velocityY;
        this.settings.decelerate = false;
        this._move();
    };
    VanillaKinetic.prototype.end = function() {
        this.settings.decelerate = true;
    };
    VanillaKinetic.prototype.stop = function() {
        this.velocity = 0;
        this.velocityY = 0;
        this.settings.decelerate = true;
        if (typeof this.settings.stopped === 'function') {
            this.settings.stopped.call(this);
        }
    };
    VanillaKinetic.prototype.detach = function() {
        this._detachListeners();
        this.el.classList.remove(this.ACTIVE_CLASS);
        this.el.style.cursor = '';
    };
    VanillaKinetic.prototype.attach = function() {
        if (this.el.classList.contains(this.ACTIVE_CLASS)) {
            return;
        }
        this._attachListeners();
        this.el.classList.add(this.ACTIVE_CLASS);
        this.el.style.cursor = this.settings.cursor;
    };
    // Internal functions
    VanillaKinetic.prototype._initElements = function() {
        this.el.classList.add(this.ACTIVE_CLASS);
        _extend(this, {
            xpos: null,
            prevXPos: false,
            ypos: null,
            prevYPos: false,
            mouseDown: false,
            throttleTimeout: 1000 / this.settings.throttleFPS,
            lastMove: null,
            elementFocused: null
        });
        this.velocity = 0;
        this.velocityY = 0;
        var that = this;
        this.documentResetHandler = function() {
            that._resetMouse.apply(that);
        };
        // FIXME make sure to remove this
        var html = document.documentElement;
        html.addEventListener("mouseup", this.documentResetHandler, false);
        html.addEventListener("click", this.documentResetHandler, false);
        this._initEvents();
        this.el.style.cursor = this.settings.cursor;
        if (this.settings.triggerHardware) {
            var prefixes = [
                '',
                '-ms-',
                '-webkit-',
                '-moz-'
            ];
            var styles = {
                'transform': 'translate3d(0,0,0)',
                'perspective': '1000',
                'backface-visibility': 'hidden'
            };
            for(var i = 0; i < prefixes.length; i++){
                var prefix = prefixes[i];
                for(var key in styles){
                    if (styles.hasOwnProperty(key)) {
                        this.el.style[prefix + key] = styles[key];
                    }
                }
            }
        }
    };
    VanillaKinetic.prototype._initEvents = function() {
        var self = this;
        this.settings.events = {
            touchStart: function(e) {
                var touch;
                if (self._useTarget(e.target, e)) {
                    touch = e.originalEvent.touches[0];
                    self.threshold = self._threshold(e.target, e);
                    self._start(touch.clientX, touch.clientY);
                    e.stopPropagation();
                }
            },
            touchMove: function(e) {
                var touch;
                if (self.mouseDown) {
                    touch = e.originalEvent.touches[0];
                    self._inputmove(touch.clientX, touch.clientY);
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                }
            },
            inputDown: function(e) {
                if (self._useTarget(e.target, e)) {
                    self.threshold = self._threshold(e.target, e);
                    self._start(e.clientX, e.clientY);
                    self.elementFocused = e.target;
                    if (e.target.nodeName === "IMG") {
                        e.preventDefault();
                    }
                    e.stopPropagation();
                }
            },
            inputEnd: function(e) {
                if (self._useTarget(e.target, e)) {
                    self._end();
                    self.elementFocused = null;
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                }
            },
            inputMove: function(e) {
                if (self.mouseDown) {
                    self._inputmove(e.clientX, e.clientY);
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                }
            },
            scroll: function(e) {
                if (typeof self.settings.moved === 'function') {
                    self.settings.moved.call(self, self.settings);
                }
                if (e.preventDefault) {
                    e.preventDefault();
                }
            },
            inputClick: function(e) {
                if (Math.abs(self.velocity) > 0 || Math.abs(self.velocityY) > 0) {
                    e.preventDefault();
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    }
                    return false;
                }
            },
            dragStart: function(e) {
                if (self._useTarget(e.target, e) && self.elementFocused) {
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    }
                    return false;
                }
            },
            selectStart: function(e) {
                if (typeof self.settings.selectStart === 'function') {
                    return self.settings.selectStart.apply(self, arguments);
                } else if (self._useTarget(e.target, e)) {
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    }
                    return false;
                }
            }
        };
        this._attachListeners();
    };
    VanillaKinetic.prototype._inputmove = function(clientX, clientY) {
        if (!this.lastMove || new Date() > new Date(this.lastMove.getTime() + this.throttleTimeout)) {
            this.lastMove = new Date();
            if (this.mouseDown && (this.xpos || this.ypos)) {
                var movedX = clientX - this.xpos;
                var movedY = clientY - this.ypos;
                if (this.settings.invert) {
                    movedX *= -1;
                    movedY *= -1;
                }
                if (this.threshold > 0) {
                    var moved = Math.sqrt(movedX * movedX + movedY * movedY);
                    if (this.threshold > moved) {
                        return;
                    } else {
                        this.threshold = 0;
                    }
                }
                if (this.elementFocused) {
                    this.elementFocused.blur();
                    this.elementFocused = null;
                    this.el.focus();
                }
                this.settings.decelerate = false;
                this.velocity = this.velocityY = 0;
                var scrollLeft = this.scrollLeft();
                var scrollTop = this.scrollTop();
                this.scrollLeft(this.settings.x ? scrollLeft - movedX : scrollLeft);
                this.scrollTop(this.settings.y ? scrollTop - movedY : scrollTop);
                this.prevXPos = this.xpos;
                this.prevYPos = this.ypos;
                this.xpos = clientX;
                this.ypos = clientY;
                this._calculateVelocities();
                this._setMoveClasses(this.settings.movingClass);
                if (typeof this.settings.moved === 'function') {
                    this.settings.moved.call(this, this.settings);
                }
            }
        }
    };
    VanillaKinetic.prototype._calculateVelocities = function() {
        this.velocity = this._capVelocity(this.prevXPos - this.xpos, this.settings.maxvelocity);
        this.velocityY = this._capVelocity(this.prevYPos - this.ypos, this.settings.maxvelocity);
        if (this.settings.invert) {
            this.velocity *= -1;
            this.velocityY *= -1;
        }
    };
    VanillaKinetic.prototype._end = function() {
        if (this.xpos && this.prevXPos && this.settings.decelerate === false) {
            this.settings.decelerate = true;
            this._calculateVelocities();
            this.xpos = this.prevXPos = this.mouseDown = false;
            this._move();
        }
    };
    VanillaKinetic.prototype._useTarget = function(target, event) {
        if (typeof this.settings.filterTarget === 'function') {
            return this.settings.filterTarget.call(this, target, event) !== false;
        }
        return true;
    };
    VanillaKinetic.prototype._threshold = function(target, event) {
        if (typeof this.settings.threshold === 'function') {
            return this.settings.threshold.call(this, target, event);
        }
        return this.settings.threshold;
    };
    VanillaKinetic.prototype._start = function(clientX, clientY) {
        this.mouseDown = true;
        this.velocity = this.prevXPos = 0;
        this.velocityY = this.prevYPos = 0;
        this.xpos = clientX;
        this.ypos = clientY;
    };
    VanillaKinetic.prototype._resetMouse = function() {
        this.xpos = false;
        this.ypos = false;
        this.mouseDown = false;
    };
    VanillaKinetic.prototype._decelerateVelocity = function(velocity, slowdown) {
        return Math.floor(Math.abs(velocity)) === 0 ? 0 // is velocity less than 1?
         : velocity * slowdown; // reduce slowdown
    };
    VanillaKinetic.prototype._capVelocity = function(velocity, max) {
        var newVelocity = velocity;
        if (velocity > 0) {
            if (velocity > max) {
                newVelocity = max;
            }
        } else {
            if (velocity < 0 - max) {
                newVelocity = 0 - max;
            }
        }
        return newVelocity;
    };
    VanillaKinetic.prototype._setMoveClasses = function(classes) {
        // The fix-me comment below is from original jQuery.kinetic project
        // FIXME: consider if we want to apply PL #44, this should not remove
        // classes we have not defined on the element!
        var settings = this.settings;
        var el = this.el;
        el.classList.remove(settings.movingClass.up);
        el.classList.remove(settings.movingClass.down);
        el.classList.remove(settings.movingClass.left);
        el.classList.remove(settings.movingClass.right);
        el.classList.remove(settings.deceleratingClass.up);
        el.classList.remove(settings.deceleratingClass.down);
        el.classList.remove(settings.deceleratingClass.left);
        el.classList.remove(settings.deceleratingClass.right);
        if (this.velocity > 0) {
            el.classList.add(classes.right);
        }
        if (this.velocity < 0) {
            el.classList.add(classes.left);
        }
        if (this.velocityY > 0) {
            el.classList.add(classes.down);
        }
        if (this.velocityY < 0) {
            el.classList.add(classes.up);
        }
    };
    VanillaKinetic.prototype._move = function() {
        var scroller = this._getScroller();
        var self = this;
        var settings = this.settings;
        if (settings.x && scroller.scrollWidth > 0) {
            this.scrollLeft(this.scrollLeft() + this.velocity);
            if (Math.abs(this.velocity) > 0) {
                this.velocity = settings.decelerate ? self._decelerateVelocity(this.velocity, settings.slowdown) : this.velocity;
            }
        } else {
            this.velocity = 0;
        }
        if (settings.y && scroller.scrollHeight > 0) {
            this.scrollTop(this.scrollTop() + this.velocityY);
            if (Math.abs(this.velocityY) > 0) {
                this.velocityY = settings.decelerate ? self._decelerateVelocity(this.velocityY, settings.slowdown) : this.velocityY;
            }
        } else {
            this.velocityY = 0;
        }
        self._setMoveClasses(settings.deceleratingClass);
        if (typeof settings.moved === 'function') {
            settings.moved.call(this, settings);
        }
        if (Math.abs(this.velocity) > 0 || Math.abs(this.velocityY) > 0) {
            if (!this.moving) {
                this.moving = true;
                // tick for next movement
                _raf(function() {
                    self.moving = false;
                    self._move();
                });
            }
        } else {
            self.stop();
        }
    };
    VanillaKinetic.prototype._getScroller = function() {
        // FIXME we may want to normalize behaviour across browsers as in original jQuery.kinetic
        // currently this won't work correctly on all brwosers when attached to html or body element
        return this.el;
    };
    VanillaKinetic.prototype.scrollLeft = function(left) {
        var scroller = this._getScroller();
        if (typeof left === 'number') {
            scroller.scrollLeft = left;
            this.settings.scrollLeft = left;
        } else {
            return scroller.scrollLeft;
        }
    };
    VanillaKinetic.prototype.scrollTop = function(top) {
        var scroller = this._getScroller();
        if (typeof top === 'number') {
            scroller.scrollTop = top;
            this.settings.scrollTop = top;
        } else {
            return scroller.scrollTop;
        }
    };
    VanillaKinetic.prototype._attachListeners = function() {
        var el = this.el;
        var settings = this.settings;
        if (_isTouch) {
            el.addEventListener('touchstart', settings.events.touchStart, false);
            el.addEventListener('touchend', settings.events.inputEnd, false);
            el.addEventListener('touchmove', settings.events.touchMove, false);
        }
        el.addEventListener('mousedown', settings.events.inputDown, false);
        el.addEventListener('mouseup', settings.events.inputEnd, false);
        el.addEventListener('mousemove', settings.events.inputMove, false);
        el.addEventListener('click', settings.events.inputClick, false);
        el.addEventListener('scroll', settings.events.scroll, false);
        el.addEventListener('selectstart', settings.events.selectStart, false);
        el.addEventListener('dragstart', settings.events.dragStart, false);
    };
    VanillaKinetic.prototype._detachListeners = function() {
        var el = this.el;
        var settings = this.settings;
        if (_isTouch) {
            el.removeEventListener('touchstart', settings.events.touchStart, false);
            el.removeEventListener('touchend', settings.events.inputEnd, false);
            el.removeEventListener('touchmove', settings.events.touchMove, false);
        }
        el.removeEventListener('mousedown', settings.events.inputDown, false);
        el.removeEventListener('mouseup', settings.events.inputEnd, false);
        el.removeEventListener('mousemove', settings.events.inputMove, false);
        el.removeEventListener('click', settings.events.inputClick, false);
        el.removeEventListener('scroll', settings.events.scroll, false);
        el.removeEventListener('selectstart', settings.events.selectStart, false);
        el.removeEventListener('dragstart', settings.events.dragStart, false);
    };
    window.VanillaKinetic = VanillaKinetic;
})();


}),
"./source/js/validation-runner.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (ValidationRunner)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");

class ValidationRunner {
    isValid(key, value, settings) {
        // Get the validation index
        let validationIndex = null;
        this.validations.some((validation, index)=>{
            if (validation.key !== key) {
                return false;
            }
            validationIndex = index;
            return true;
        });
        if (validationIndex === null) {
            return true;
        }
        // Run the validation
        const dummyChanges = {};
        dummyChanges[key] = value;
        const proxier = createSettingsProxier(settings, dummyChanges, this);
        return !this._runValidation(validationIndex, value, proxier);
    }
    validate(settings) {
        this._validateOptions({}, settings);
    }
    getValidatedOptions(settings, options) {
        const cloned = Object.assign({}, options);
        this._validateOptions(settings, cloned);
        return cloned;
    }
    _validateOptions(settings, options) {
        const settingsProxier = createSettingsProxier(settings, options, this);
        this._applyValidations(options, settingsProxier);
    }
    _applyValidations(options, proxier) {
        this.validations.forEach((validation, index)=>{
            if (!options.hasOwnProperty(validation.key)) {
                return;
            }
            const input = options[validation.key];
            const corrected = this._runValidation(index, input, proxier);
            if (corrected) {
                if (!corrected.warningSuppressed) {
                    emitWarning(validation.key, input, corrected.value);
                }
                options[validation.key] = corrected.value;
            }
        }, this);
    }
    _runValidation(index, input, proxier) {
        const validation = this.validations[index];
        proxier.index = index;
        let warningSuppressed = false;
        const config = {
            suppressWarning: ()=>{
                warningSuppressed = true;
            }
        };
        const outputValue = validation.validate(input, proxier.proxy, config);
        if (outputValue === undefined || outputValue === input) {
            return null;
        }
        return {
            value: outputValue,
            warningSuppressed: warningSuppressed
        };
    }
    constructor(options){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "whitelistedKeys", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "additionalProperties", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "validations", void 0);
        this.whitelistedKeys = options.whitelistedKeys || [];
        this.additionalProperties = options.additionalProperties || [];
        this.validations = options.validations;
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
 */ function createSettingsProxier(settings, options, runner) {
    const proxier = {
        proxy: {},
        index: null
    };
    const lookup = lookupValue.bind(null, settings, options);
    const properties = {};
    runner.whitelistedKeys.forEach((whitelisted)=>{
        properties[whitelisted] = {
            get: lookup.bind(null, whitelisted)
        };
    });
    runner.additionalProperties.forEach((additional)=>{
        properties[additional.key] = {
            get: additional.get
        };
    });
    runner.validations.forEach((validation, validationIndex)=>{
        properties[validation.key] = {
            get: ()=>{
                if (validationIndex < proxier.index) {
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
function emitWarning(key, original, corrected) {
    console.warn('Invalid value for ' + key + ': ' + original + '. Using ' + corrected + ' instead.');
}
function lookupValue(base, extension, key) {
    if (key in extension) {
        return extension[key];
    }
    return base[key];
}


}),
"./source/js/viewer-core.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (ViewerCore)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");
/* ESM import */var _utils_elt__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./source/js/utils/elt.ts");
/* ESM import */var _utils_get_scrollbar_width__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__("./source/js/utils/get-scrollbar-width.ts");
/* ESM import */var _gesture_events__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__("./source/js/gesture-events.ts");
/* ESM import */var _diva_global__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__("./source/js/diva-global.ts");
/* ESM import */var _document_handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__("./source/js/document-handler.ts");
/* ESM import */var _grid_handler__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__("./source/js/grid-handler.ts");
/* ESM import */var _page_overlay_manager__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__("./source/js/page-overlay-manager.ts");
/* ESM import */var _renderer__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__("./source/js/renderer.ts");
/* ESM import */var _page_layouts__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__("./source/js/page-layouts/index.ts");
/* ESM import */var _validation_runner__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__("./source/js/validation-runner.ts");
/* ESM import */var _viewport__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__("./source/js/viewport.ts");













const debug = __webpack_require__("./node_modules/debug/src/browser.js")('diva:ViewerCore');
function generateId() {
    return generateId.counter++;
}
generateId.counter = 1;
function createSettingsView(sources) {
    const obj = {};
    sources.forEach((source)=>{
        registerMixin(obj, source);
    });
    // @ts-ignore
    return obj;
}
function registerMixin(obj, mixin) {
    Object.keys(mixin).forEach((key)=>{
        Object.defineProperty(obj, key, {
            get: ()=>{
                return mixin[key];
            },
            set: ()=>{
                // TODO: Make everything strict mode so this isn't needed
                throw new TypeError('Cannot set settings.' + key);
            }
        });
    });
}
function arraysEqual(a, b) {
    if (a.length !== b.length) {
        return false;
    }
    for(let i = 0, len = a.length; i < len; i++){
        if (a[i] !== b[i]) {
            return false;
        }
    }
    return true;
}
// Define validations
const optionsValidations = [
    {
        key: 'goDirectlyTo',
        validate: (value, settings)=>{
            if (value < 0 || value >= settings.manifest.pages.length) {
                return 0;
            }
            return value;
        }
    },
    {
        key: 'minPagesPerRow',
        validate: (value)=>{
            return Math.max(2, value);
        }
    },
    {
        key: 'maxPagesPerRow',
        validate: (value, settings)=>{
            return Math.max(value, settings.minPagesPerRow);
        }
    },
    {
        key: 'pagesPerRow',
        validate: (value, settings)=>{
            // Default to the maximum
            if (value < settings.minPagesPerRow || value > settings.maxPagesPerRow) {
                return settings.maxPagesPerRow;
            }
            return value;
        }
    },
    {
        key: 'maxZoomLevel',
        validate: (value, settings, config)=>{
            // Changing this value isn't really an error, it just depends on the
            // source manifest
            config.suppressWarning();
            if (value < 0 || value > settings.manifest.maxZoom) {
                return settings.manifest.maxZoom;
            }
            return value;
        }
    },
    {
        key: 'minZoomLevel',
        validate: (value, settings, config)=>{
            // Changes based on the manifest value shouldn't trigger a
            // warning
            if (value > settings.manifest.maxZoom) {
                config.suppressWarning();
                return 0;
            }
            if (value < 0 || value > settings.maxZoomLevel) {
                return 0;
            }
            return value;
        }
    },
    {
        key: 'zoomLevel',
        validate: (value, settings, config)=>{
            if (value > settings.manifest.maxZoom) {
                config.suppressWarning();
                return 0;
            }
            if (value < settings.minZoomLevel || value > settings.maxZoomLevel) {
                return settings.minZoomLevel;
            }
            return value;
        }
    }
];
class ViewerCore {
    isValidOption(key, value) {
        return this.optionsValidator.isValid(key, value, this.viewerState.options);
    }
    elemAttrs(ident, base) {
        const attrs = {
            id: this.settings.ID + ident,
            class: 'diva-' + ident
        };
        if (base) {
            return Object.assign(attrs, base);
        } else {
            return attrs;
        }
    }
    getPageData(pageIndex, attribute) {
        return this.settings.manifest.pages[pageIndex].d[this.settings.zoomLevel][attribute];
    }
    // Reset some settings and empty the viewport
    clearViewer() {
        this.viewerState.viewport.top = 0;
        // Clear all the timeouts to prevent undesired pages from loading
        clearTimeout(this.viewerState.resizeTimer);
    }
    hasChangedOption(options, key) {
        return key in options && options[key] !== this.settings[key];
    }
    //Shortcut for closing fullscreen with the escape key
    escapeListener(e) {
        if (e.code === 'Escape') {
            this.publicInstance.leaveFullscreenMode();
        }
    }
    /**
     * Update settings to match the specified options. Load the viewer,
     * fire appropriate events for changed options.
     */ reloadViewer(newOptions) {
        const queuedEvents = [];
        newOptions = this.optionsValidator.getValidatedOptions(this.settings, newOptions);
        // Set the zoom level if valid and fire a ZoomLevelDidChange event
        if (this.hasChangedOption(newOptions, 'zoomLevel')) {
            this.viewerState.oldZoomLevel = this.settings.zoomLevel;
            this.viewerState.options.zoomLevel = newOptions.zoomLevel;
            queuedEvents.push([
                "ZoomLevelDidChange",
                newOptions.zoomLevel
            ]);
        }
        // Set the pages per row if valid and fire an event
        if (this.hasChangedOption(newOptions, 'pagesPerRow')) {
            this.viewerState.options.pagesPerRow = newOptions.pagesPerRow;
            queuedEvents.push([
                "GridRowNumberDidChange",
                newOptions.pagesPerRow
            ]);
        }
        // Update verticallyOriented (no event fired)
        if (this.hasChangedOption(newOptions, 'verticallyOriented')) this.viewerState.options.verticallyOriented = newOptions.verticallyOriented;
        // Show/Hide non-paged pages
        if (this.hasChangedOption(newOptions, 'showNonPagedPages')) {
            this.viewerState.options.showNonPagedPages = newOptions.showNonPagedPages;
        }
        // Update page position (no event fired here)
        if ('goDirectlyTo' in newOptions) {
            this.viewerState.options.goDirectlyTo = newOptions.goDirectlyTo;
            if ('verticalOffset' in newOptions) {
                this.viewerState.verticalOffset = newOptions.verticalOffset;
            }
            if ('horizontalOffset' in newOptions) {
                this.viewerState.horizontalOffset = newOptions.horizontalOffset;
            }
        } else {
            // Otherwise the default is to remain on the current page
            this.viewerState.options.goDirectlyTo = this.settings.activePageIndex;
        }
        if (this.hasChangedOption(newOptions, 'inGrid') || this.hasChangedOption(newOptions, 'inBookLayout')) {
            if ('inGrid' in newOptions) {
                this.viewerState.options.inGrid = newOptions.inGrid;
            }
            if ('inBookLayout' in newOptions) {
                this.viewerState.options.inBookLayout = newOptions.inBookLayout;
            }
            queuedEvents.push([
                "ViewDidSwitch",
                this.settings.inGrid
            ]);
        }
        // Note: prepareModeChange() depends on inGrid and the vertical/horizontalOffset (for now)
        if (this.hasChangedOption(newOptions, 'inFullscreen')) {
            this.viewerState.options.inFullscreen = newOptions.inFullscreen;
            this.prepareModeChange(newOptions);
            queuedEvents.push([
                "ModeDidSwitch",
                this.settings.inFullscreen
            ]);
        }
        this.clearViewer();
        this.updateViewHandlerAndRendering();
        if (this.viewerState.renderer) {
            // TODO: The usage of padding variables is still really
            // messy and inconsistent
            const rendererConfig = {
                pageLayouts: (0,_page_layouts__WEBPACK_IMPORTED_MODULE_8__["default"])(this.settings),
                padding: this.getPadding(),
                maxZoomLevel: this.settings.inGrid ? null : this.viewerState.manifest.maxZoom,
                verticallyOriented: this.settings.verticallyOriented || this.settings.inGrid
            };
            const viewportPosition = {
                zoomLevel: this.settings.inGrid ? null : this.settings.zoomLevel,
                anchorPage: this.settings.goDirectlyTo,
                verticalOffset: this.viewerState.verticalOffset,
                horizontalOffset: this.viewerState.horizontalOffset
            };
            const sourceProvider = this.getCurrentSourceProvider();
            if (debug.enabled) {
                const serialized = Object.keys(rendererConfig).filter(function(key) {
                    // Too long
                    return key !== 'pageLayouts' && key !== 'padding';
                }).map(function(key) {
                    const value = rendererConfig[key];
                    return key + ': ' + JSON.stringify(value);
                }).join(', ');
                debug('reload with %s', serialized);
            }
            this.viewerState.renderer.load(rendererConfig, viewportPosition, sourceProvider);
        }
        queuedEvents.forEach((params)=>{
            this.publish.apply(this, params);
        });
        return true;
    }
    // Handles switching in and out of fullscreen mode
    prepareModeChange(options) {
        // Toggle the classes
        const changeClass = options.inFullscreen ? 'add' : 'remove';
        this.viewerState.outerObject.classList[changeClass]('diva-fullscreen');
        document.body.classList[changeClass]('diva-hide-scrollbar');
        this.settings.parentObject.classList[changeClass]('diva-full-width');
        // Adjust Diva's internal panel size, keeping the old values
        const storedHeight = this.settings.panelHeight;
        const storedWidth = this.settings.panelWidth;
        this.viewerState.viewport.invalidate();
        // If this isn't the original load, the offsets matter, and the position isn't being changed...
        if (!this.viewerState.loaded && !this.settings.inGrid && !('verticalOffset' in options)) {
            //get the updated panel size
            const newHeight = this.settings.panelHeight;
            const newWidth = this.settings.panelWidth;
            //and re-center the new panel on the same point
            this.viewerState.verticalOffset += (storedHeight - newHeight) / 2;
            this.viewerState.horizontalOffset += (storedWidth - newWidth) / 2;
        }
        //turn on/off escape key listener
        if (options.inFullscreen) document.addEventListener('keyup', this.boundEscapeListener);
        else document.removeEventListener('keyup', this.boundEscapeListener);
    }
    // Update the view handler and the view rendering for the current view
    updateViewHandlerAndRendering() {
        const Handler = this.settings.inGrid ? _grid_handler__WEBPACK_IMPORTED_MODULE_5__["default"] : _document_handler__WEBPACK_IMPORTED_MODULE_4__["default"];
        if (this.viewerState.viewHandler && !(this.viewerState.viewHandler instanceof Handler)) {
            this.viewerState.viewHandler.destroy();
            this.viewerState.viewHandler = null;
        }
        if (!this.viewerState.viewHandler) {
            this.viewerState.viewHandler = new Handler(this);
        }
        if (!this.viewerState.renderer) {
            this.initializeRenderer();
        }
    }
    // TODO: This could probably be done upon ViewerCore initialization
    initializeRenderer() {
        const compatErrors = _renderer__WEBPACK_IMPORTED_MODULE_7__["default"].getCompatibilityErrors();
        if (compatErrors) {
            this.showError(compatErrors);
        } else {
            const options = {
                viewport: this.viewerState.viewport,
                outerElement: this.viewerState.outerElement,
                innerElement: this.viewerState.innerElement,
                settings: this.settings
            };
            const hooks = {
                onViewWillLoad: ()=>{
                    this.viewerState.viewHandler.onViewWillLoad();
                },
                onViewDidLoad: ()=>{
                    this.updatePageOverlays();
                    this.viewerState.viewHandler.onViewDidLoad();
                },
                onViewDidUpdate: (pages, targetPage)=>{
                    this.updatePageOverlays();
                    this.viewerState.viewHandler.onViewDidUpdate(pages, targetPage);
                },
                onViewDidTransition: ()=>{
                    this.updatePageOverlays();
                },
                onPageWillLoad: (pageIndex)=>{
                    this.publish('PageWillLoad', pageIndex);
                },
                onZoomLevelWillChange: (zoomLevel)=>{
                    this.publish('ZoomLevelWillChange', zoomLevel);
                }
            };
            this.viewerState.renderer = new _renderer__WEBPACK_IMPORTED_MODULE_7__["default"](options, hooks);
        }
    }
    getCurrentSourceProvider() {
        if (this.settings.inGrid) {
            const gridSourceProvider = {
                getAllZoomLevelsForPage: (page)=>{
                    return [
                        gridSourceProvider.getBestZoomLevelForPage(page)
                    ];
                },
                getBestZoomLevelForPage: (page)=>{
                    const url = this.settings.manifest.getPageImageURL(page.index, {
                        width: page.dimensions.width
                    });
                    return {
                        zoomLevel: 1,
                        rows: 1,
                        cols: 1,
                        tiles: [
                            {
                                url: url,
                                zoomLevel: 1,
                                row: 0,
                                col: 0,
                                dimensions: page.dimensions,
                                offset: {
                                    top: 0,
                                    left: 0
                                }
                            }
                        ]
                    };
                }
            };
            return gridSourceProvider;
        }
        const tileDimensions = {
            width: this.settings.tileWidth,
            height: this.settings.tileHeight
        };
        return {
            getBestZoomLevelForPage: (page)=>{
                return this.settings.manifest.getPageImageTiles(page.index, Math.ceil(this.settings.zoomLevel), tileDimensions);
            },
            getAllZoomLevelsForPage: (page)=>{
                const levels = [];
                const levelCount = this.viewerState.manifest.maxZoom;
                for(let level = 0; level <= levelCount; level++){
                    levels.push(this.settings.manifest.getPageImageTiles(page.index, level, tileDimensions));
                }
                levels.reverse();
                return levels;
            }
        };
    }
    getPadding() {
        let topPadding, leftPadding;
        let docVPadding, docHPadding;
        if (this.settings.inGrid) {
            docVPadding = this.settings.fixedPadding;
            topPadding = leftPadding = docHPadding = 0;
        } else {
            topPadding = this.settings.verticallyOriented ? this.viewerState.verticalPadding : 0;
            leftPadding = this.settings.verticallyOriented ? 0 : this.viewerState.horizontalPadding;
            docVPadding = this.settings.verticallyOriented ? 0 : this.viewerState.verticalPadding;
            docHPadding = this.settings.verticallyOriented ? this.viewerState.horizontalPadding : 0;
        }
        return {
            document: {
                top: docVPadding,
                bottom: docVPadding,
                left: docHPadding,
                right: docHPadding
            },
            page: {
                top: topPadding,
                bottom: 0,
                left: leftPadding,
                right: 0
            }
        };
    }
    updatePageOverlays() {
        this.viewerState.pageOverlays.updateOverlays(this.viewerState.renderer.getRenderedPages());
    }
    // Called to handle any zoom level
    handleZoom(newZoomLevel, focalPoint) {
        // If the zoom level provided is invalid, return false
        if (!this.isValidOption('zoomLevel', newZoomLevel)) {
            return false;
        }
        // While zooming, don't update scroll offsets based on the scaled version of diva-inner
        this.viewerState.viewportObject.removeEventListener('scroll', this.boundScrollFunction);
        // If no focal point was given, zoom on the center of the viewport
        if (!focalPoint) {
            const viewport = this.viewerState.viewport;
            const currentRegion = this.viewerState.renderer.layout.getPageRegion(this.settings.activePageIndex);
            focalPoint = {
                anchorPage: this.settings.activePageIndex,
                offset: {
                    left: viewport.width / 2 - (currentRegion.left - viewport.left),
                    top: viewport.height / 2 - (currentRegion.top - viewport.top)
                }
            };
        }
        const pageRegion = this.viewerState.renderer.layout.getPageRegion(focalPoint.anchorPage);
        // calculate distance from cursor coordinates to center of viewport
        const focalXToCenter = pageRegion.left + focalPoint.offset.left - (this.settings.viewport.left + this.settings.viewport.width / 2);
        const focalYToCenter = pageRegion.top + focalPoint.offset.top - (this.settings.viewport.top + this.settings.viewport.height / 2);
        const getPositionForZoomLevel = (zoomLevel, initZoom)=>{
            const zoomRatio = Math.pow(2, zoomLevel - initZoom);
            //TODO(jeromepl): Calculate position from page top left to viewport top left
            // calculate horizontal/verticalOffset: distance from viewport center to page upper left corner
            const horizontalOffset = focalPoint.offset.left * zoomRatio - focalXToCenter;
            const verticalOffset = focalPoint.offset.top * zoomRatio - focalYToCenter;
            return {
                zoomLevel: zoomLevel,
                anchorPage: focalPoint.anchorPage,
                verticalOffset: verticalOffset,
                horizontalOffset: horizontalOffset
            };
        };
        this.viewerState.options.zoomLevel = newZoomLevel;
        let initialZoomLevel = this.viewerState.oldZoomLevel;
        this.viewerState.oldZoomLevel = this.settings.zoomLevel;
        const endPosition = getPositionForZoomLevel(newZoomLevel, initialZoomLevel);
        this.viewerState.options.goDirectlyTo = endPosition.anchorPage;
        this.viewerState.verticalOffset = endPosition.verticalOffset;
        this.viewerState.horizontalOffset = endPosition.horizontalOffset;
        this.viewerState.renderer.transitionViewportPosition({
            duration: this.settings.zoomDuration,
            parameters: {
                zoomLevel: {
                    from: initialZoomLevel,
                    to: newZoomLevel
                }
            },
            getPosition: (parameters)=>{
                return getPositionForZoomLevel(parameters.zoomLevel, initialZoomLevel);
            },
            onEnd: (info)=>{
                this.viewerState.viewportObject.addEventListener('scroll', this.boundScrollFunction);
                if (info.interrupted) {
                    this.viewerState.oldZoomLevel = newZoomLevel;
                }
            }
        });
        // Deactivate zoom buttons while zooming
        let zoomInButton = document.getElementById(this.settings.selector + 'zoom-in-button');
        let zoomOutButton = document.getElementById(this.settings.selector + 'zoom-out-button');
        zoomInButton.disabled = true;
        zoomOutButton.disabled = true;
        setTimeout(()=>{
            zoomInButton.disabled = false;
            zoomOutButton.disabled = false;
        }, this.settings.zoomDuration);
        // Send off the zoom level did change event.
        this.publish("ZoomLevelDidChange", newZoomLevel);
        return true;
    }
    /*
     Gets the Y-offset for a specific point on a specific page
     Acceptable values for "anchor":
     "top" (default) - will anchor top of the page to the top of the diva-outer element
     "bottom" - top, s/top/bottom
     "center" - will center the page on the diva element
     Returned value will be the distance from the center of the diva-outer element to the top of the current page for the specified anchor
     */ getYOffset(pageIndex, anchor) {
        let pidx = typeof pageIndex === "undefined" ? this.settings.activePageIndex : pageIndex;
        if (anchor === "center" || anchor === "centre") {
            return Math.floor(this.getPageData(pidx, "h") / 2);
        } else if (anchor === "bottom") {
            return Math.floor(this.getPageData(pidx, "h") - this.settings.panelHeight / 2);
        } else {
            return Math.floor(this.settings.panelHeight / 2);
        }
    }
    //Same as getYOffset with "left" and "right" as acceptable values instead of "top" and "bottom"
    getXOffset(pageIndex, anchor) {
        let pidx = typeof pageIndex === "undefined" ? this.settings.activePageIndex : pageIndex;
        if (anchor === "left") {
            return Math.floor(this.settings.panelWidth / 2);
        } else if (anchor === "right") {
            return Math.floor(this.getPageData(pidx, "w") - this.settings.panelWidth / 2);
        } else {
            return Math.floor(this.getPageData(pidx, "w") / 2);
        }
    }
    // updates panelHeight/panelWidth on resize
    updatePanelSize() {
        this.viewerState.viewport.invalidate();
        // FIXME(wabain): This should really only be called after initial load
        if (this.viewerState.renderer) {
            this.updateOffsets();
            this.viewerState.renderer.goto(this.settings.activePageIndex, this.viewerState.verticalOffset, this.viewerState.horizontalOffset);
        }
        return true;
    }
    updateOffsets() {
        const pageOffset = this.viewerState.renderer.layout.getPageToViewportCenterOffset(this.settings.activePageIndex, this.viewerState.viewport);
        if (pageOffset) {
            this.viewerState.horizontalOffset = pageOffset.x;
            this.viewerState.verticalOffset = pageOffset.y;
        }
    }
    // Bind mouse events (drag to scroll, double-click)
    bindMouseEvents() {
        // Set drag scroll on the viewport object
        this.viewerState.viewportObject.classList.add('dragscroll');
        _gesture_events__WEBPACK_IMPORTED_MODULE_2__["default"].onDoubleClick(this.viewerState.viewportObject, (event, coords)=>{
            debug('Double click at %s, %s', coords.left, coords.top);
            this.viewerState.viewHandler.onDoubleClick(event, coords);
        });
    }
    onResize() {
        this.updatePanelSize();
        // Cancel any previously-set resize timeouts
        clearTimeout(this.viewerState.resizeTimer);
        this.viewerState.resizeTimer = setTimeout(()=>{
            const pageOffset = this.viewerState.renderer.layout.getPageToViewportCenterOffset(this.settings.activePageIndex, this.viewerState.viewport);
            if (pageOffset) {
                this.reloadViewer({
                    goDirectlyTo: this.settings.activePageIndex,
                    verticalOffset: pageOffset.y,
                    horizontalOffset: pageOffset.x
                });
            } else {
                this.reloadViewer({
                    goDirectlyTo: this.settings.activePageIndex
                });
            }
        }, 200);
    }
    // Bind touch and orientation change events
    bindTouchEvents() {
        // Block the user from moving the window only if it's not integrated
        if (this.settings.blockMobileMove) {
            document.body.addEventListener('touchmove', (event)=>{
                event.preventDefault();
                return false;
            });
        }
        // Touch events for swiping in the viewport to scroll pages
        // this.viewerState.viewportObject.addEventListener('scroll', this.scrollFunction.bind(this));
        _gesture_events__WEBPACK_IMPORTED_MODULE_2__["default"].onPinch(this.viewerState.viewportObject, (event, coords, start, end)=>{
            debug('Pinch %s at %s, %s', end - start, coords.left, coords.top);
            this.viewerState.viewHandler.onPinch(event, coords, start, end);
        });
        _gesture_events__WEBPACK_IMPORTED_MODULE_2__["default"].onDoubleTap(this.viewerState.viewportObject, (event, coords)=>{
            debug('Double tap at %s, %s', coords.left, coords.top);
            this.viewerState.viewHandler.onDoubleClick(event, coords);
        });
    }
    // Handle the scroll
    scrollFunction() {
        const previousTopScroll = this.viewerState.viewport.top;
        const previousLeftScroll = this.viewerState.viewport.left;
        let direction;
        this.viewerState.viewport.invalidate();
        const newScrollTop = this.viewerState.viewport.top;
        const newScrollLeft = this.viewerState.viewport.left;
        if (this.settings.verticallyOriented || this.settings.inGrid) {
            direction = newScrollTop - previousTopScroll;
        } else {
            direction = newScrollLeft - previousLeftScroll;
        }
        this.viewerState.renderer.adjust();
        const primaryScroll = this.settings.verticallyOriented || this.settings.inGrid ? newScrollTop : newScrollLeft;
        this.publish("ViewerDidScroll", primaryScroll);
        if (direction > 0) {
            this.publish("ViewerDidScrollDown", primaryScroll);
        } else if (direction < 0) {
            this.publish("ViewerDidScrollUp", primaryScroll);
        }
        this.updateOffsets();
    }
    // Binds most of the event handlers (some more in createToolbar)
    handleEvents() {
        // Change the cursor for dragging
        this.viewerState.innerObject.addEventListener('mousedown', ()=>{
            this.viewerState.innerObject.classList.add('diva-grabbing');
        });
        this.viewerState.innerObject.addEventListener('mouseup', ()=>{
            this.viewerState.innerObject.classList.remove('diva-grabbing');
        });
        this.bindMouseEvents();
        this.viewerState.viewportObject.addEventListener('scroll', this.boundScrollFunction);
        const upArrowKey = 38, downArrowKey = 40, leftArrowKey = 37, rightArrowKey = 39, spaceKey = 32, pageUpKey = 33, pageDownKey = 34, homeKey = 36, endKey = 35;
        // Catch the key presses in document
        document.addEventListener('keydown.diva', (event)=>{
            if (!this.viewerState.isActiveDiva) {
                return true;
            }
            // Space or page down - go to the next page
            if (this.settings.enableSpaceScroll && !event.shiftKey && event.keyCode === spaceKey || this.settings.enableKeyScroll && event.keyCode === pageDownKey) {
                this.viewerState.viewport.top += this.settings.panelHeight;
                return false;
            } else if (!this.settings.enableSpaceScroll && event.keyCode === spaceKey) {
                event.preventDefault();
            }
            if (this.settings.enableKeyScroll) {
                // Don't steal keyboard shortcuts (metaKey = command [OS X], super [Win/Linux])
                if (event.shiftKey || event.ctrlKey || event.metaKey) {
                    return true;
                }
                switch(event.keyCode){
                    case pageUpKey:
                        // Page up - go to the previous page
                        this.viewerState.viewport.top -= this.settings.panelHeight;
                        return false;
                    case upArrowKey:
                        // Up arrow - scroll up
                        this.viewerState.viewport.top -= this.settings.arrowScrollAmount;
                        return false;
                    case downArrowKey:
                        // Down arrow - scroll down
                        this.viewerState.viewport.top += this.settings.arrowScrollAmount;
                        return false;
                    case leftArrowKey:
                        // Left arrow - scroll left
                        this.viewerState.viewport.left -= this.settings.arrowScrollAmount;
                        return false;
                    case rightArrowKey:
                        // Right arrow - scroll right
                        this.viewerState.viewport.left += this.settings.arrowScrollAmount;
                        return false;
                    case homeKey:
                        // Home key - go to the beginning of the document
                        this.viewerState.viewport.top = 0;
                        return false;
                    case endKey:
                        // End key - go to the end of the document
                        // Count on the viewport coordinate value being normalized
                        if (this.settings.verticallyOriented) {
                            this.viewerState.viewport.top = Infinity;
                        } else {
                            this.viewerState.viewport.left = Infinity;
                        }
                        return false;
                    default:
                        return true;
                }
            }
            return true;
        });
        _diva_global__WEBPACK_IMPORTED_MODULE_3__["default"].Events.subscribe('ViewerDidTerminate', ()=>{
            document.removeEventListener('keydown.diva');
        }, this.settings.ID);
        // this.bindTouchEvents();
        // Handle window resizing events
        window.addEventListener('resize', this.onResize.bind(this), false);
        _diva_global__WEBPACK_IMPORTED_MODULE_3__["default"].Events.subscribe('ViewerDidTerminate', function() {
            window.removeEventListener('resize', this.onResize, false);
        }, this.settings.ID);
        // Handle orientation change separately
        if ('onorientationchange' in window) {
            window.addEventListener('orientationchange', this.onResize, false);
            _diva_global__WEBPACK_IMPORTED_MODULE_3__["default"].Events.subscribe('ViewerDidTerminate', function() {
                window.removeEventListener('orientationchange', this.onResize, false);
            }, this.settings.ID);
        }
        _diva_global__WEBPACK_IMPORTED_MODULE_3__["default"].Events.subscribe('PanelSizeDidChange', this.updatePanelSize, this.settings.ID);
        // Clear page and resize timeouts when the viewer is destroyed
        _diva_global__WEBPACK_IMPORTED_MODULE_3__["default"].Events.subscribe('ViewerDidTerminate', ()=>{
            if (this.viewerState.renderer) {
                this.viewerState.renderer.destroy();
            }
            clearTimeout(this.viewerState.resizeTimer);
        }, this.settings.ID);
    }
    initPlugins() {
        if (!this.settings.hasOwnProperty('plugins')) {
            return null;
        }
        this.viewerState.pluginInstances = this.settings.plugins.map((plugin)=>{
            const p = new plugin(this);
            if (p.isPageTool) {
                this.viewerState.pageTools.push(p);
            }
            return p;
        });
    }
    showThrobber() {
        this.hideThrobber();
        this.viewerState.throbberTimeoutID = setTimeout(()=>{
            let thb = document.getElementById(this.settings.selector + 'throbber');
            if (thb) thb.style.display = 'block';
        }, this.settings.throbberTimeout);
    }
    hideThrobber() {
        // Clear the timeout, if it hasn't executed yet
        clearTimeout(this.viewerState.throbberTimeoutID);
        let thb = document.getElementById(this.settings.selector + 'throbber');
        // Hide the throbber if it has already executed
        if (thb) {
            thb.style.display = 'none';
        }
    }
    showError(message) {
        const errorElement = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', this.elemAttrs('error'), [
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('button', this.elemAttrs('error-close', {
                'aria-label': 'Close dialog'
            })),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('p', (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('strong', 'Error')),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', message)
        ]);
        this.viewerState.outerObject.appendChild(errorElement);
        // Bind dialog close button
        document.getElementById(this.settings.selector + 'error-close').addEventListener('click', ()=>{
            errorElement.parentNode.removeChild(errorElement);
        });
    }
    setManifest(manifest, loadOptions) {
        this.viewerState.manifest = manifest;
        this.hideThrobber();
        // Convenience value
        this.viewerState.numPages = this.settings.manifest.pages.length;
        this.optionsValidator.validate(this.viewerState.options);
        this.publish('NumberOfPagesDidChange', this.settings.numPages);
        // Calculate the horizontal and vertical inter-page padding based on the dimensions of the average zoom level
        if (this.settings.adaptivePadding > 0) {
            const z = Math.floor((this.settings.minZoomLevel + this.settings.maxZoomLevel) / 2);
            this.viewerState.horizontalPadding = Math.floor(this.settings.manifest.getAverageWidth(z) * this.settings.adaptivePadding);
            this.viewerState.verticalPadding = Math.floor(this.settings.manifest.getAverageHeight(z) * this.settings.adaptivePadding);
        } else {
            // It's less than or equal to 0; use fixedPadding instead
            this.viewerState.horizontalPadding = this.settings.fixedPadding;
            this.viewerState.verticalPadding = this.settings.fixedPadding;
        }
        // Make sure the vertical padding is at least 40, if plugin icons are enabled
        if (this.viewerState.pageTools.length) {
            this.viewerState.verticalPadding = Math.max(40, this.viewerState.verticalPadding);
        }
        // If we detect a viewingHint of 'paged' in the manifest or sequence, enable book view by default
        if (this.settings.manifest.paged) {
            this.viewerState.options.inBookLayout = true;
        }
        // Plugin setup hooks should be bound to the ObjectDidLoad event
        this.publish('ObjectDidLoad', this.settings);
        // Adjust the document panel dimensions
        this.updatePanelSize();
        let needsXCoord, needsYCoord;
        let anchoredVertically = false;
        let anchoredHorizontally = false;
        // NB: `==` here will check both null and undefined
        if (loadOptions.goDirectlyTo == null) {
            loadOptions.goDirectlyTo = this.settings.goDirectlyTo;
            needsXCoord = needsYCoord = true;
        } else {
            needsXCoord = loadOptions.horizontalOffset == null || isNaN(loadOptions.horizontalOffset);
            needsYCoord = loadOptions.verticalOffset == null || isNaN(loadOptions.verticalOffset);
        }
        // Set default values for the horizontal and vertical offsets
        if (needsXCoord) {
            // FIXME: What if inBookLayout/verticallyOriented is changed by loadOptions?
            if (loadOptions.goDirectlyTo === 0 && this.settings.inBookLayout && this.settings.verticallyOriented) {
                // if in book layout, center the first opening by default
                loadOptions.horizontalOffset = this.viewerState.horizontalPadding;
            } else {
                anchoredHorizontally = true;
                loadOptions.horizontalOffset = this.getXOffset(loadOptions.goDirectlyTo, "center");
            }
        }
        if (needsYCoord) {
            anchoredVertically = true;
            loadOptions.verticalOffset = this.getYOffset(loadOptions.goDirectlyTo, "top");
        }
        this.reloadViewer(loadOptions);
        //prep dimensions one last time now that pages have loaded
        this.updatePanelSize();
        if (this.settings.enableAutoTitle) {
            let title = document.getElementById(this.settings.selector + 'title');
            if (title) {
                title.innerHTML = this.settings.manifest.itemTitle;
            } else {
                this.settings.parentObject.insertBefore((0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', this.elemAttrs('title'), [
                    this.settings.manifest.itemTitle
                ]), this.settings.parentObject.firstChild);
            }
        }
        // FIXME: This is a hack to ensure that the outerElement scrollbars are taken into account
        if (this.settings.verticallyOriented) {
            this.viewerState.innerElement.style.minWidth = this.settings.panelWidth + 'px';
        } else {
            this.viewerState.innerElement.style.minHeight = this.settings.panelHeight + 'px';
        }
        // FIXME: If the page was supposed to be positioned relative to the viewport we need to
        // recalculate it to take into account the scrollbars
        if (anchoredVertically || anchoredHorizontally) {
            if (anchoredVertically) {
                this.viewerState.verticalOffset = this.getYOffset(this.settings.activePageIndex, "top");
            }
            if (anchoredHorizontally) {
                this.viewerState.horizontalOffset = this.getXOffset(this.settings.activePageIndex, "center");
            }
            this.viewerState.renderer.goto(this.settings.activePageIndex, this.viewerState.verticalOffset, this.viewerState.horizontalOffset);
        }
        // signal that everything should be set up and ready to go.
        this.viewerState.loaded = true;
        this.publish("ViewerDidLoad", this.settings);
    }
    publish(event) {
        for(var _len = arguments.length, args = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++){
            args[_key - 1] = arguments[_key];
        }
        // const args = Array.prototype.slice.call(arguments, 1);
        _diva_global__WEBPACK_IMPORTED_MODULE_3__["default"].Events.publish(event, args, this.publicInstance);
    }
    getSettings() {
        return this.settings;
    }
    // Temporary accessor for the state of the viewer core
    // TODO: Replace this with a more restricted view of whatever needs
    // be exposed through settings for backwards compat
    getInternalState() {
        return this.viewerState;
    }
    getPublicInstance() {
        return this.publicInstance;
    }
    getPageTools() {
        return this.viewerState.pageTools;
    }
    getCurrentLayout() {
        return this.viewerState.renderer ? this.viewerState.renderer.layout : null;
    }
    /** Get a copy of the current viewport dimensions */ getViewport() {
        const viewport = this.viewerState.viewport;
        return {
            top: viewport.top,
            left: viewport.left,
            bottom: viewport.bottom,
            right: viewport.right,
            width: viewport.width,
            height: viewport.height
        };
    }
    addPageOverlay(overlay) {
        this.viewerState.pageOverlays.addOverlay(overlay);
    }
    removePageOverlay(overlay) {
        this.viewerState.pageOverlays.removeOverlay(overlay);
    }
    getPageRegion(pageIndex, options) {
        const layout = this.viewerState.renderer.layout;
        const region = layout.getPageRegion(pageIndex, options);
        if (options && options.incorporateViewport) {
            const secondaryDim = this.settings.verticallyOriented ? 'width' : 'height';
            if (this.viewerState.viewport[secondaryDim] > layout.dimensions[secondaryDim]) {
                const docOffset = (this.viewerState.viewport[secondaryDim] - layout.dimensions[secondaryDim]) / 2;
                if (this.settings.verticallyOriented) {
                    return {
                        top: region.top,
                        bottom: region.bottom,
                        left: region.left + docOffset,
                        right: region.right + docOffset
                    };
                } else {
                    return {
                        top: region.top + docOffset,
                        bottom: region.bottom + docOffset,
                        left: region.left,
                        right: region.right
                    };
                }
            }
        }
        return region;
    }
    getPagePositionAtViewportOffset(coords) {
        const docCoords = {
            left: coords.left + this.viewerState.viewport.left,
            top: coords.top + this.viewerState.viewport.top
        };
        const renderer = this.viewerState.renderer;
        const renderedPages = renderer.getRenderedPages();
        const pageCount = renderedPages.length;
        // Find the page on which the coords occur
        for(let i = 0; i < pageCount; i++){
            const pageIndex = renderedPages[i];
            const region = renderer.layout.getPageRegion(pageIndex);
            if (region.left <= docCoords.left && region.right >= docCoords.left && region.top <= docCoords.top && region.bottom >= docCoords.top) {
                return {
                    anchorPage: pageIndex,
                    offset: {
                        left: docCoords.left - region.left,
                        top: docCoords.top - region.top
                    }
                };
            }
        }
        // Fall back to current page
        // FIXME: Would be better to use the closest page or something
        const currentRegion = renderer.layout.getPageRegion(this.settings.activePageIndex);
        return {
            anchorPage: this.settings.activePageIndex,
            offset: {
                left: docCoords.left - currentRegion.left,
                top: docCoords.top - currentRegion.top
            }
        };
    }
    // setManifest (manifest, loadOptions)
    // {
    //     setManifest(manifest, loadOptions || {});
    // }
    /**
     * Set the current page to the given index, firing VisiblePageDidChange
     *
     * @param activePage
     * @param visiblePages
     */ setCurrentPages(activePage, visiblePages) {
        if (!arraysEqual(this.viewerState.currentPageIndices, visiblePages)) {
            this.viewerState.currentPageIndices = visiblePages;
            if (this.viewerState.activePageIndex !== activePage) {
                this.viewerState.activePageIndex = activePage;
                this.publish("ActivePageDidChange", activePage);
            }
            this.publish("VisiblePageDidChange", visiblePages);
            // Publish an event if the page we're switching to has other images.
            if (this.viewerState.manifest.pages[activePage].otherImages.length > 0) {
                this.publish('VisiblePageHasAlternateViews', activePage);
            }
        } else if (this.viewerState.activePageIndex !== activePage) {
            this.viewerState.activePageIndex = activePage;
            this.publish("ActivePageDidChange", activePage);
        }
    }
    getPageName(pageIndex) {
        return this.viewerState.manifest.pages[pageIndex].f;
    }
    reload(newOptions) {
        return this.reloadViewer(newOptions);
    }
    zoom(zoomLevel, focalPoint) {
        return this.handleZoom(zoomLevel, focalPoint);
    }
    enableScrollable() {
        if (!this.viewerState.isScrollable) {
            this.bindMouseEvents();
            this.enableDragScrollable();
            this.viewerState.options.enableKeyScroll = this.viewerState.initialKeyScroll;
            this.viewerState.options.enableSpaceScroll = this.viewerState.initialSpaceScroll;
            this.viewerState.viewportElement.style.overflow = 'auto';
            this.viewerState.isScrollable = true;
        }
    }
    enableDragScrollable() {
        if (this.viewerState.viewportObject.hasAttribute('nochilddrag')) {
            this.viewerState.viewportObject.removeAttribute('nochilddrag');
        }
    }
    disableScrollable() {
        if (this.viewerState.isScrollable) {
            // block dragging
            this.disableDragScrollable();
            // block double-click zooming
            this.viewerState.outerObject.ondblclick = null;
            this.viewerState.outerObject.oncontextmenu = null;
            // disable all other scrolling actions
            this.viewerState.viewportElement.style.overflow = 'hidden';
            // block scrolling keys behavior, respecting initial scroll settings
            this.viewerState.initialKeyScroll = this.settings.enableKeyScroll;
            this.viewerState.initialSpaceScroll = this.settings.enableSpaceScroll;
            this.viewerState.options.enableKeyScroll = false;
            this.viewerState.options.enableSpaceScroll = false;
            this.viewerState.isScrollable = false;
        }
    }
    disableDragScrollable() {
        if (!this.viewerState.viewportObject.hasAttribute('nochilddrag')) {
            this.viewerState.viewportObject.setAttribute('nochilddrag', "");
        }
    }
    // isValidOption (key, value)
    // {
    //     return isValidOption(key, value);
    // }
    // getXOffset (pageIndex, xAnchor)
    // {
    //     return getXOffset(pageIndex, xAnchor);
    // }
    // getYOffset (pageIndex, yAnchor)
    // {
    //     return getYOffset(pageIndex, yAnchor);
    // }
    // this.publish = publish;
    clear() {
        this.clearViewer();
    }
    setPendingManifestRequest(pendingManifestRequest) {
        this.viewerState.pendingManifestRequest = pendingManifestRequest;
    }
    destroy() {
        // Useful event to access elements in diva before they get destroyed. Used by the highlight plugin.
        this.publish('ViewerWillTerminate', this.settings);
        // Cancel any pending request retrieving a manifest
        if (this.settings.pendingManifestRequest) {
            this.settings.pendingManifestRequest.abort();
        }
        // Removes the hide-scrollbar class from the body
        document.body.classList.remove('diva-hide-scrollbar');
        // Empty the parent container and remove any diva-related data
        this.settings.parentObject.parentElement.replaceChildren();
        // Remove any additional styling on the parent element
        this.settings.parentObject.parentElement.removeAttribute('style');
        this.settings.parentObject.parentElement.removeAttribute('class');
        this.publish('ViewerDidTerminate', this.settings);
        // Clear the Events cache
        _diva_global__WEBPACK_IMPORTED_MODULE_3__["default"].Events.unsubscribeAll(this.settings.ID);
    }
    constructor(element, options, publicInstance){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__._)(this, "parentObject", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__._)(this, "publicInstance", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__._)(this, "viewerState", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__._)(this, "settings", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__._)(this, "optionsValidator", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__._)(this, "boundScrollFunction", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_11__._)(this, "boundEscapeListener", void 0);
        this.parentObject = element;
        this.publicInstance = publicInstance;
        // Things that cannot be changed because of the way they are used by the script
        // Many of these are declared with arbitrary values that are changed later on
        this.viewerState = {
            currentPageIndices: [],
            activePageIndex: 0,
            horizontalOffset: 0,
            horizontalPadding: 0,
            ID: null,
            initialKeyScroll: false,
            initialSpaceScroll: false,
            innerElement: null,
            innerObject: null,
            isActiveDiva: true,
            isScrollable: true,
            isZooming: false,
            loaded: false,
            manifest: null,
            mobileWebkit: false,
            numPages: 0,
            oldZoomLevel: -1,
            options: options,
            outerElement: null,
            outerObject: null,
            pageOverlays: new _page_overlay_manager__WEBPACK_IMPORTED_MODULE_6__["default"](),
            pageTools: [],
            parentObject: this.parentObject,
            pendingManifestRequest: null,
            pluginInstances: [],
            renderer: null,
            resizeTimer: null,
            scrollbarWidth: 0,
            selector: '',
            throbberTimeoutID: null,
            toolbar: null,
            verticalOffset: 0,
            verticalPadding: 0,
            viewHandler: null,
            viewport: null,
            viewportElement: null,
            viewportObject: null,
            zoomDuration: 400
        };
        this.settings = createSettingsView([
            options,
            this.viewerState
        ]);
        // Generate an ID that can be used as a prefix for all the other IDs
        const idNumber = generateId();
        this.viewerState.ID = 'diva-' + idNumber + '-';
        this.viewerState.selector = this.settings.ID;
        // Aliases for compatibility
        Object.defineProperties(this.settings, {
            // Height of the document viewer pane
            panelHeight: {
                get: ()=>{
                    return this.viewerState.viewport.height;
                }
            },
            // Width of the document viewer pane
            panelWidth: {
                get: ()=>{
                    return this.viewerState.viewport.width;
                }
            }
        });
        this.optionsValidator = new _validation_runner__WEBPACK_IMPORTED_MODULE_9__["default"]({
            additionalProperties: [
                {
                    key: 'manifest',
                    get: ()=>{
                        return this.viewerState.manifest;
                    }
                }
            ],
            validations: optionsValidations
        });
        this.viewerState.scrollbarWidth = (0,_utils_get_scrollbar_width__WEBPACK_IMPORTED_MODULE_1__["default"])();
        // If window.orientation is defined, then it's probably mobileWebkit
        this.viewerState.mobileWebkit = window.screen.orientation !== undefined;
        if (options.hashParamSuffix === null) {
            // Omit the suffix from the first instance
            if (idNumber === 1) {
                options.hashParamSuffix = '';
            } else {
                options.hashParamSuffix = idNumber + '';
            }
        }
        // Create the inner and outer panels
        const innerElem = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', this.elemAttrs('inner', {
            class: 'diva-inner'
        }));
        const viewportElem = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', this.elemAttrs('viewport'), innerElem);
        const outerElem = (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', this.elemAttrs('outer'), viewportElem, (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', this.elemAttrs('throbber'), [
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube1'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube2'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube3'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube4'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube5'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube6'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube7'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube8'
            }),
            (0,_utils_elt__WEBPACK_IMPORTED_MODULE_0__.elt)('div', {
                class: 'cube cube9'
            })
        ]));
        this.viewerState.innerElement = innerElem;
        this.viewerState.viewportElement = viewportElem;
        this.viewerState.outerElement = outerElem;
        this.viewerState.innerObject = innerElem;
        this.viewerState.viewportObject = viewportElem;
        this.viewerState.outerObject = outerElem;
        this.settings.parentObject.append(outerElem);
        this.viewerState.viewport = new _viewport__WEBPACK_IMPORTED_MODULE_10__["default"](this.viewerState.viewportElement, {
            intersectionTolerance: this.settings.viewportMargin
        });
        this.boundScrollFunction = this.scrollFunction.bind(this);
        this.boundEscapeListener = this.escapeListener.bind(this);
        // Do all the plugin initialisation
        this.initPlugins();
        this.handleEvents();
        // Show the throbber while waiting for the manifest to load
        this.showThrobber();
    }
}



}),
"./source/js/viewport.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
"use strict";
__webpack_require__.r(__webpack_exports__);
__webpack_require__.d(__webpack_exports__, {
  "default": () => (Viewport)
});
/* ESM import */var _swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__("./node_modules/@swc/helpers/esm/_define_property.js");

class Viewport {
    intersectsRegion(region) {
        return this.hasHorizontalOverlap(region) && this.hasVerticalOverlap(region);
    }
    hasVerticalOverlap(region) {
        const top = this.top - this.intersectionTolerance;
        const bottom = this.bottom + this.intersectionTolerance;
        return fallsBetween(region.top, top, bottom) || fallsBetween(region.bottom, top, bottom) || region.top <= top && region.bottom >= bottom;
    }
    hasHorizontalOverlap(region) {
        const left = this.left - this.intersectionTolerance;
        const right = this.right + this.intersectionTolerance;
        return fallsBetween(region.left, left, right) || fallsBetween(region.right, left, right) || region.left <= left && region.right >= right;
    }
    invalidate() {
        // FIXME: Should this check the inner dimensions as well?
        this._width = this.outer.clientWidth;
        this._height = this.outer.clientHeight;
        this._top = this.outer.scrollTop;
        this._left = this.outer.scrollLeft;
    }
    setInnerDimensions(dimensions) {
        this._innerDimensions = dimensions;
        if (dimensions) {
            this._top = clamp(this._top, 0, dimensions.height - this._height);
            this._left = clamp(this._left, 0, dimensions.width - this._width);
        }
    }
    constructor(outer, options){
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "intersectionTolerance", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "outer", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_top", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_left", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_width", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_height", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "_innerDimensions", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "top", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "bottom", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "left", void 0);
        (0,_swc_helpers_define_property__WEBPACK_IMPORTED_MODULE_0__._)(this, "right", void 0);
        options = options || {};
        this.intersectionTolerance = options.intersectionTolerance || 0;
        this.outer = outer;
        this._top = this._left = this._width = this._height = this._innerDimensions = null;
        this.invalidate();
    }
}

Object.defineProperties(Viewport.prototype, {
    top: getCoordinateDescriptor('top', 'height'),
    left: getCoordinateDescriptor('left', 'width'),
    width: getDimensionDescriptor('width'),
    height: getDimensionDescriptor('height'),
    bottom: {
        get: function() {
            return this._top + this._height;
        }
    },
    right: {
        get: function() {
            return this._left + this._width;
        }
    }
});
function getCoordinateDescriptor(coord, associatedDimension) {
    const privateProp = '_' + coord;
    const source = 'scroll' + coord.charAt(0).toUpperCase() + coord.slice(1);
    return {
        get: function() {
            return this[privateProp];
        },
        set: function(newValue) {
            let normalized;
            if (this._innerDimensions) {
                const maxAllowed = this._innerDimensions[associatedDimension] - this[associatedDimension];
                normalized = clamp(newValue, 0, maxAllowed);
            } else {
                normalized = clampMin(newValue, 0);
            }
            this[privateProp] = this.outer[source] = normalized;
        }
    };
}
function getDimensionDescriptor(dimen) {
    return {
        get: function() {
            return this['_' + dimen];
        }
    };
}
function fallsBetween(point, start, end) {
    return point >= start && point <= end;
}
function clamp(value, min, max) {
    return clampMin(clampMax(value, max), min);
}
function clampMin(value, min) {
    return Math.max(value, min);
}
function clampMax(value, max) {
    return Math.min(value, max);
}


}),

});
/************************************************************************/
// The module cache
var __webpack_module_cache__ = {};

// The require function
function __webpack_require__(moduleId) {

// Check if module is in cache
var cachedModule = __webpack_module_cache__[moduleId];
if (cachedModule !== undefined) {
if (cachedModule.error !== undefined) throw cachedModule.error;
return cachedModule.exports;
}
// Create a new module (and put it into the cache)
var module = (__webpack_module_cache__[moduleId] = {
id: moduleId,
exports: {}
});
// Execute the module function
try {

var execOptions = { id: moduleId, module: module, factory: __webpack_modules__[moduleId], require: __webpack_require__ };
__webpack_require__.i.forEach(function(handler) { handler(execOptions); });
module = execOptions.module;
if (!execOptions.factory) {
  console.error("undefined factory", moduleId)
}
execOptions.factory.call(module.exports, module, module.exports, execOptions.require);

} catch (e) {
module.error = e;
throw e;
}
// Return the exports of the module
return module.exports;

}

// expose the modules object (__webpack_modules__)
__webpack_require__.m = __webpack_modules__;

// expose the module cache
__webpack_require__.c = __webpack_module_cache__;

// expose the module execution interceptor
__webpack_require__.i = [];

/************************************************************************/
// webpack/runtime/compat_get_default_export
(() => {
// getDefaultExport function for compatibility with non-ESM modules
__webpack_require__.n = (module) => {
	var getter = module && module.__esModule ?
		() => (module['default']) :
		() => (module);
	__webpack_require__.d(getter, { a: getter });
	return getter;
};

})();
// webpack/runtime/define_property_getters
(() => {
__webpack_require__.d = (exports, definition) => {
	for(var key in definition) {
        if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
            Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
        }
    }
};
})();
// webpack/runtime/get mini-css chunk filename
(() => {
// This function allow to reference chunks
__webpack_require__.miniCssF = (chunkId) => {
  // return url for filenames not based on template
  
  // return url for filenames based on template
  return "" + chunkId + ".css"
}
})();
// webpack/runtime/get_chunk_update_filename
(() => {
__webpack_require__.hu = (chunkId) => ('' + chunkId + '.' + __webpack_require__.h() + '.hot-update.js')
})();
// webpack/runtime/get_full_hash
(() => {
__webpack_require__.h = () => ("7fd0a270a955f1d9")
})();
// webpack/runtime/get_main_filename/update manifest
(() => {
__webpack_require__.hmrF = function () {
            return "diva." + __webpack_require__.h() + ".hot-update.json";
         };
        
})();
// webpack/runtime/has_own_property
(() => {
__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
})();
// webpack/runtime/hot_module_replacement
(() => {
var currentModuleData = {};
var installedModules = __webpack_require__.c;

// module and require creation
var currentChildModule;
var currentParents = [];

// status
var registeredStatusHandlers = [];
var currentStatus = "idle";

// while downloading
var blockingPromises = 0;
var blockingPromisesWaiting = [];

// The update info
var currentUpdateApplyHandlers;
var queuedInvalidatedModules;

__webpack_require__.hmrD = currentModuleData;
__webpack_require__.i.push(function (options) {
	var module = options.module;
	var require = createRequire(options.require, options.id);
	module.hot = createModuleHotObject(options.id, module);
	module.parents = currentParents;
	module.children = [];
	currentParents = [];
	options.require = require;
});

__webpack_require__.hmrC = {};
__webpack_require__.hmrI = {};

function createRequire(require, moduleId) {
	var me = installedModules[moduleId];
	if (!me) return require;
	var fn = function (request) {
		if (me.hot.active) {
			if (installedModules[request]) {
				var parents = installedModules[request].parents;
				if (parents.indexOf(moduleId) === -1) {
					parents.push(moduleId);
				}
			} else {
				currentParents = [moduleId];
				currentChildModule = request;
			}
			if (me.children.indexOf(request) === -1) {
				me.children.push(request);
			}
		} else {
			console.warn(
				"[HMR] unexpected require(" +
				request +
				") from disposed module " +
				moduleId
			);
			currentParents = [];
		}
		return require(request);
	};
	var createPropertyDescriptor = function (name) {
		return {
			configurable: true,
			enumerable: true,
			get: function () {
				return require[name];
			},
			set: function (value) {
				require[name] = value;
			}
		};
	};
	for (var name in require) {
		if (Object.prototype.hasOwnProperty.call(require, name) && name !== "e") {
			Object.defineProperty(fn, name, createPropertyDescriptor(name));
		}
	}

	fn.e = function (chunkId, fetchPriority) {
		return trackBlockingPromise(require.e(chunkId, fetchPriority));
	};

	return fn;
}

function createModuleHotObject(moduleId, me) {
	var _main = currentChildModule !== moduleId;
	var hot = {
		_acceptedDependencies: {},
		_acceptedErrorHandlers: {},
		_declinedDependencies: {},
		_selfAccepted: false,
		_selfDeclined: false,
		_selfInvalidated: false,
		_disposeHandlers: [],
		_main: _main,
		_requireSelf: function () {
			currentParents = me.parents.slice();
			currentChildModule = _main ? undefined : moduleId;
			__webpack_require__(moduleId);
		},
		active: true,
		accept: function (dep, callback, errorHandler) {
			if (dep === undefined) hot._selfAccepted = true;
			else if (typeof dep === "function") hot._selfAccepted = dep;
			else if (typeof dep === "object" && dep !== null) {
				for (var i = 0; i < dep.length; i++) {
					hot._acceptedDependencies[dep[i]] = callback || function () { };
					hot._acceptedErrorHandlers[dep[i]] = errorHandler;
				}
			} else {
				hot._acceptedDependencies[dep] = callback || function () { };
				hot._acceptedErrorHandlers[dep] = errorHandler;
			}
		},
		decline: function (dep) {
			if (dep === undefined) hot._selfDeclined = true;
			else if (typeof dep === "object" && dep !== null)
				for (var i = 0; i < dep.length; i++)
					hot._declinedDependencies[dep[i]] = true;
			else hot._declinedDependencies[dep] = true;
		},
		dispose: function (callback) {
			hot._disposeHandlers.push(callback);
		},
		addDisposeHandler: function (callback) {
			hot._disposeHandlers.push(callback);
		},
		removeDisposeHandler: function (callback) {
			var idx = hot._disposeHandlers.indexOf(callback);
			if (idx >= 0) hot._disposeHandlers.splice(idx, 1);
		},
		invalidate: function () {
			this._selfInvalidated = true;
			switch (currentStatus) {
				case "idle":
					currentUpdateApplyHandlers = [];
					Object.keys(__webpack_require__.hmrI).forEach(function (key) {
						__webpack_require__.hmrI[key](moduleId, currentUpdateApplyHandlers);
					});
					setStatus("ready");
					break;
				case "ready":
					Object.keys(__webpack_require__.hmrI).forEach(function (key) {
						__webpack_require__.hmrI[key](moduleId, currentUpdateApplyHandlers);
					});
					break;
				case "prepare":
				case "check":
				case "dispose":
				case "apply":
					(queuedInvalidatedModules = queuedInvalidatedModules || []).push(
						moduleId
					);
					break;
				default:
					break;
			}
		},
		check: hotCheck,
		apply: hotApply,
		status: function (l) {
			if (!l) return currentStatus;
			registeredStatusHandlers.push(l);
		},
		addStatusHandler: function (l) {
			registeredStatusHandlers.push(l);
		},
		removeStatusHandler: function (l) {
			var idx = registeredStatusHandlers.indexOf(l);
			if (idx >= 0) registeredStatusHandlers.splice(idx, 1);
		},
		data: currentModuleData[moduleId]
	};
	currentChildModule = undefined;
	return hot;
}

function setStatus(newStatus) {
	currentStatus = newStatus; 
	var results = [];
	for (var i = 0; i < registeredStatusHandlers.length; i++)
		results[i] = registeredStatusHandlers[i].call(null, newStatus);

	return Promise.all(results).then(function () { });
}

function unblock() {
	if (--blockingPromises === 0) {
		setStatus("ready").then(function () {
			if (blockingPromises === 0) {
				var list = blockingPromisesWaiting;
				blockingPromisesWaiting = [];
				for (var i = 0; i < list.length; i++) {
					list[i]();
				}
			}
		});
	}
}

function trackBlockingPromise(promise) {
	switch (currentStatus) {
		case "ready":
			setStatus("prepare");
		case "prepare":
			blockingPromises++;
			promise.then(unblock, unblock);
			return promise;
		default:
			return promise;
	}
}

function waitForBlockingPromises(fn) {
	if (blockingPromises === 0) return fn();
	return new Promise(function (resolve) {
		blockingPromisesWaiting.push(function () {
			resolve(fn());
		});
	});
}

function hotCheck(applyOnUpdate) {
	if (currentStatus !== "idle") {
		throw new Error("check() is only allowed in idle status");
	} 
	return setStatus("check")
		.then(__webpack_require__.hmrM)
		.then(function (update) {
			if (!update) {
				return setStatus(applyInvalidatedModules() ? "ready" : "idle").then(
					function () {
						return null;
					}
				);
			}

			return setStatus("prepare").then(function () {
				var updatedModules = [];
				currentUpdateApplyHandlers = [];

				return Promise.all(
					Object.keys(__webpack_require__.hmrC).reduce(function (
						promises,
						key
					) {
						__webpack_require__.hmrC[key](
							update.c,
							update.r,
							update.m,
							promises,
							currentUpdateApplyHandlers,
							updatedModules
						);
						return promises;
					},
						[])
				).then(function () {
					return waitForBlockingPromises(function () {
						if (applyOnUpdate) {
							return internalApply(applyOnUpdate);
						}
						return setStatus("ready").then(function () {
							return updatedModules;
						});
					});
				});
			});
		});
}

function hotApply(options) {
	if (currentStatus !== "ready") {
		return Promise.resolve().then(function () {
			throw new Error(
				"apply() is only allowed in ready status (state: " + currentStatus + ")"
			);
		});
	}
	return internalApply(options);
}

function internalApply(options) {
	options = options || {};
	applyInvalidatedModules();
	var results = currentUpdateApplyHandlers.map(function (handler) {
		return handler(options);
	});
	currentUpdateApplyHandlers = undefined;
	var errors = results
		.map(function (r) {
			return r.error;
		})
		.filter(Boolean);

	if (errors.length > 0) {
		return setStatus("abort").then(function () {
			throw errors[0];
		});
	}

	var disposePromise = setStatus("dispose");

	results.forEach(function (result) {
		if (result.dispose) result.dispose();
	});

	var applyPromise = setStatus("apply");

	var error;
	var reportError = function (err) {
		if (!error) error = err;
	};

	var outdatedModules = [];
	results.forEach(function (result) {
		if (result.apply) {
			var modules = result.apply(reportError);
			if (modules) {
				for (var i = 0; i < modules.length; i++) {
					outdatedModules.push(modules[i]);
				}
			}
		}
	});

	return Promise.all([disposePromise, applyPromise]).then(function () {
		if (error) {
			return setStatus("fail").then(function () {
				throw error;
			});
		}

		if (queuedInvalidatedModules) {
			return internalApply(options).then(function (list) {
				outdatedModules.forEach(function (moduleId) {
					if (list.indexOf(moduleId) < 0) list.push(moduleId);
				});
				return list;
			});
		}

		return setStatus("idle").then(function () {
			return outdatedModules;
		});
	});
}

function applyInvalidatedModules() {
	if (queuedInvalidatedModules) {
		if (!currentUpdateApplyHandlers) currentUpdateApplyHandlers = [];
		Object.keys(__webpack_require__.hmrI).forEach(function (key) {
			queuedInvalidatedModules.forEach(function (moduleId) {
				__webpack_require__.hmrI[key](moduleId, currentUpdateApplyHandlers);
			});
		});
		queuedInvalidatedModules = undefined;
		return true;
	}
}

})();
// webpack/runtime/load_script
(() => {
var inProgress = {};

var dataWebpackPrefix = "diva.js:";
// loadScript function to load a script via script tag
__webpack_require__.l = function (url, done, key, chunkId) {
	if (inProgress[url]) {
		inProgress[url].push(done);
		return;
	}
	var script, needAttach;
	if (key !== undefined) {
		var scripts = document.getElementsByTagName("script");
		for (var i = 0; i < scripts.length; i++) {
			var s = scripts[i];
			if (s.getAttribute("src") == url || s.getAttribute("data-webpack") == dataWebpackPrefix + key) {
				script = s;
				break;
			}
		}
	}
	if (!script) {
		needAttach = true;
		
    script = document.createElement('script');
    
		script.charset = 'utf-8';
		script.timeout = 120;
		if (__webpack_require__.nc) {
			script.setAttribute("nonce", __webpack_require__.nc);
		}
		script.setAttribute("data-webpack", dataWebpackPrefix + key);
		
		script.src = url;
		
    
	}
	inProgress[url] = [done];
	var onScriptComplete = function (prev, event) {
		script.onerror = script.onload = null;
		clearTimeout(timeout);
		var doneFns = inProgress[url];
		delete inProgress[url];
		script.parentNode && script.parentNode.removeChild(script);
		doneFns &&
			doneFns.forEach(function (fn) {
				return fn(event);
			});
		if (prev) return prev(event);
	};
	var timeout = setTimeout(
		onScriptComplete.bind(null, undefined, {
			type: 'timeout',
			target: script
		}),
		120000
	);
	script.onerror = onScriptComplete.bind(null, script.onerror);
	script.onload = onScriptComplete.bind(null, script.onload);
	needAttach && document.head.appendChild(script);
};

})();
// webpack/runtime/make_namespace_object
(() => {
// define __esModule on exports
__webpack_require__.r = (exports) => {
	if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
		Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
	}
	Object.defineProperty(exports, '__esModule', { value: true });
};
})();
// webpack/runtime/on_chunk_loaded
(() => {
var deferred = [];
__webpack_require__.O = (result, chunkIds, fn, priority) => {
	if (chunkIds) {
		priority = priority || 0;
		for (var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--)
			deferred[i] = deferred[i - 1];
		deferred[i] = [chunkIds, fn, priority];
		return;
	}
	var notFulfilled = Infinity;
	for (var i = 0; i < deferred.length; i++) {
		var [chunkIds, fn, priority] = deferred[i];
		var fulfilled = true;
		for (var j = 0; j < chunkIds.length; j++) {
			if (
				(priority & (1 === 0) || notFulfilled >= priority) &&
				Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))
			) {
				chunkIds.splice(j--, 1);
			} else {
				fulfilled = false;
				if (priority < notFulfilled) notFulfilled = priority;
			}
		}
		if (fulfilled) {
			deferred.splice(i--, 1);
			var r = fn();
			if (r !== undefined) result = r;
		}
	}
	return result;
};

})();
// webpack/runtime/public_path
(() => {
__webpack_require__.p = "/";
})();
// webpack/runtime/rspack_version
(() => {
__webpack_require__.rv = () => ("1.2.8")
})();
// webpack/runtime/css loading
(() => {
if (typeof document === "undefined") return;
var createStylesheet = function (
	chunkId, fullhref, oldTag, resolve, reject
) {
	var linkTag = document.createElement("link");
	
	linkTag.rel = "stylesheet";
	linkTag.type="text/css";
	if (__webpack_require__.nc) {
		linkTag.nonce = __webpack_require__.nc;
	}
	var onLinkComplete = function (event) {
		// avoid mem leaks.
		linkTag.onerror = linkTag.onload = null;
		if (event.type === 'load') {
			resolve();
		} else {
			var errorType = event && (event.type === 'load' ? 'missing' : event.type);
			var realHref = event && event.target && event.target.href || fullhref;
			var err = new Error("Loading CSS chunk " + chunkId + " failed.\\n(" + realHref + ")");
			err.code = "CSS_CHUNK_LOAD_FAILED";
			err.type = errorType;
			err.request = realHref;
			if (linkTag.parentNode) linkTag.parentNode.removeChild(linkTag)
			reject(err);
		}
	}

	linkTag.onerror = linkTag.onload = onLinkComplete;
	linkTag.href = fullhref;
	
	if (oldTag) {
  oldTag.parentNode.insertBefore(linkTag, oldTag.nextSibling);
} else {
  document.head.appendChild(linkTag);
}
	return linkTag;
}
var findStylesheet = function (href, fullhref) {
	var existingLinkTags = document.getElementsByTagName("link");
	for (var i = 0; i < existingLinkTags.length; i++) {
		var tag = existingLinkTags[i];
		var dataHref = tag.getAttribute("data-href") || tag.getAttribute("href");
		if (tag.rel === "stylesheet" && (dataHref === href || dataHref === fullhref)) return tag;
	}

	var existingStyleTags = document.getElementsByTagName("style");
	for (var i = 0; i < existingStyleTags.length; i++) {
		var tag = existingStyleTags[i];
		var dataHref = tag.getAttribute("data-href");
		if (dataHref === href || dataHref === fullhref) return tag;
	}
}

var loadStylesheet = function (chunkId) {
	return new Promise(function (resolve, reject) {
		var href = __webpack_require__.miniCssF(chunkId);
		var fullhref = __webpack_require__.p + href;
		if (findStylesheet(href, fullhref)) return resolve();
		createStylesheet(chunkId, fullhref, null, resolve, reject);
	})
}

// no chunk loading
var oldTags = [];
var newTags = [];
var applyHandler = function (options) {
	return {
		dispose: function () {
			for (var i = 0; i < oldTags.length; i++) {
				var oldTag = oldTags[i];
				if (oldTag.parentNode) oldTag.parentNode.removeChild(oldTag);
			}
			oldTags.length = 0;
		},
		apply: function () {
			for (var i = 0; i < newTags.length; i++) newTags[i].rel = "stylesheet";
			newTags.length = 0;
		}
	}
}
__webpack_require__.hmrC.miniCss = function (chunkIds, removedChunks, removedModules, promises, applyHandlers, updatedModulesList) {
	applyHandlers.push(applyHandler);
	chunkIds.forEach(function (chunkId) {
		var href = __webpack_require__.miniCssF(chunkId);
		var fullhref = __webpack_require__.p + href;
		var oldTag = findStylesheet(href, fullhref);
		if (!oldTag) return;
		promises.push(new Promise(function (resolve, reject) {
			var tag = createStylesheet(
				chunkId,
				fullhref,
				oldTag,
				function () {
					tag.as = "style";
					tag.rel = "preload";
					resolve();
				},
				reject
			);
			oldTags.push(oldTag);
			newTags.push(tag);
		}))
	});
}


})();
// webpack/runtime/jsonp_chunk_loading
(() => {

      // object to store loaded and loading chunks
      // undefined = chunk not loaded, null = chunk preloaded/prefetched
      // [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
      var installedChunks = __webpack_require__.hmrS_jsonp = __webpack_require__.hmrS_jsonp || {"diva": 0,};
      var currentUpdatedModulesList;
var waitingUpdateResolves = {};
function loadUpdateChunk(chunkId, updatedModulesList) {
	currentUpdatedModulesList = updatedModulesList;
	return new Promise((resolve, reject) => {
		waitingUpdateResolves[chunkId] = resolve;
		// start update chunk loading
		var url = __webpack_require__.p + __webpack_require__.hu(chunkId);
		// create error before stack unwound to get useful stacktrace later
		var error = new Error();
		var loadingEnded = (event) => {
			if (waitingUpdateResolves[chunkId]) {
				waitingUpdateResolves[chunkId] = undefined;
				var errorType =
					event && (event.type === 'load' ? 'missing' : event.type);
				var realSrc = event && event.target && event.target.src;
				error.message =
					'Loading hot update chunk ' +
					chunkId +
					' failed.\n(' +
					errorType +
					': ' +
					realSrc +
					')';
				error.name = 'ChunkLoadError';
				error.type = errorType;
				error.request = realSrc;
				reject(error);
			}
		};
		__webpack_require__.l(url, loadingEnded);
	});
}

self["webpackHotUpdatediva_js"] = (chunkId, moreModules, runtime) => {
	for (var moduleId in moreModules) {
		if (__webpack_require__.o(moreModules, moduleId)) {
			currentUpdate[moduleId] = moreModules[moduleId];
			if (currentUpdatedModulesList) currentUpdatedModulesList.push(moduleId);
		}
	}
	if (runtime) currentUpdateRuntime.push(runtime);
	if (waitingUpdateResolves[chunkId]) {
		waitingUpdateResolves[chunkId]();
		waitingUpdateResolves[chunkId] = undefined;
	}
};
var currentUpdateChunks;
var currentUpdate;
var currentUpdateRemovedChunks;
var currentUpdateRuntime;
function applyHandler(options) {
	if (__webpack_require__.f) delete __webpack_require__.f.jsonpHmr;
	currentUpdateChunks = undefined;
	function getAffectedModuleEffects(updateModuleId) {
		var outdatedModules = [updateModuleId];
		var outdatedDependencies = {};
		var queue = outdatedModules.map(function (id) {
			return {
				chain: [id],
				id: id
			};
		});
		while (queue.length > 0) {
			var queueItem = queue.pop();
			var moduleId = queueItem.id;
			var chain = queueItem.chain;
			var module = __webpack_require__.c[moduleId];
			if (
				!module ||
				(module.hot._selfAccepted && !module.hot._selfInvalidated)
			) {
				continue;
			}

			if (module.hot._selfDeclined) {
				return {
					type: "self-declined",
					chain: chain,
					moduleId: moduleId
				};
			}

			if (module.hot._main) {
				return {
					type: "unaccepted",
					chain: chain,
					moduleId: moduleId
				};
			}

			for (var i = 0; i < module.parents.length; i++) {
				var parentId = module.parents[i];
				var parent = __webpack_require__.c[parentId];
				if (!parent) {
					continue;
				}
				if (parent.hot._declinedDependencies[moduleId]) {
					return {
						type: "declined",
						chain: chain.concat([parentId]),
						moduleId: moduleId,
						parentId: parentId
					};
				}
				if (outdatedModules.indexOf(parentId) !== -1) {
					continue;
				}
				if (parent.hot._acceptedDependencies[moduleId]) {
					if (!outdatedDependencies[parentId]) {
						outdatedDependencies[parentId] = [];
					}
					addAllToSet(outdatedDependencies[parentId], [moduleId]);
					continue;
				}
				delete outdatedDependencies[parentId];
				outdatedModules.push(parentId);
				queue.push({
					chain: chain.concat([parentId]),
					id: parentId
				});
			}
		}

		return {
			type: "accepted",
			moduleId: updateModuleId,
			outdatedModules: outdatedModules,
			outdatedDependencies: outdatedDependencies
		};
	}

	function addAllToSet(a, b) {
		for (var i = 0; i < b.length; i++) {
			var item = b[i];
			if (a.indexOf(item) === -1) a.push(item);
		}
	}

	var outdatedDependencies = {};
	var outdatedModules = [];
	var appliedUpdate = {};

	var warnUnexpectedRequire = function warnUnexpectedRequire(module) {
		console.warn(
			"[HMR] unexpected require(" + module.id + ") to disposed module"
		);
	};

	for (var moduleId in currentUpdate) {
		if (__webpack_require__.o(currentUpdate, moduleId)) {
			var newModuleFactory = currentUpdate[moduleId];
			var result = newModuleFactory ? getAffectedModuleEffects(moduleId) : {
				type: "disposed",
				moduleId: moduleId
			};
			var abortError = false;
			var doApply = false;
			var doDispose = false;
			var chainInfo = "";
			if (result.chain) {
				chainInfo = "\nUpdate propagation: " + result.chain.join(" -> ");
			}
			switch (result.type) {
				case "self-declined":
					if (options.onDeclined) options.onDeclined(result);
					if (!options.ignoreDeclined)
						abortError = new Error(
							"Aborted because of self decline: " + result.moduleId + chainInfo
						);
					break;
				case "declined":
					if (options.onDeclined) options.onDeclined(result);
					if (!options.ignoreDeclined)
						abortError = new Error(
							"Aborted because of declined dependency: " +
							result.moduleId +
							" in " +
							result.parentId +
							chainInfo
						);
					break;
				case "unaccepted":
					if (options.onUnaccepted) options.onUnaccepted(result);
					if (!options.ignoreUnaccepted)
						abortError = new Error(
							"Aborted because " + moduleId + " is not accepted" + chainInfo
						);
					break;
				case "accepted":
					if (options.onAccepted) options.onAccepted(result);
					doApply = true;
					break;
				case "disposed":
					if (options.onDisposed) options.onDisposed(result);
					doDispose = true;
					break;
				default:
					throw new Error("Unexception type " + result.type);
			}
			if (abortError) {
				return {
					error: abortError
				};
			}
			if (doApply) {
				appliedUpdate[moduleId] = newModuleFactory;
				addAllToSet(outdatedModules, result.outdatedModules);
				for (moduleId in result.outdatedDependencies) {
					if (__webpack_require__.o(result.outdatedDependencies, moduleId)) {
						if (!outdatedDependencies[moduleId])
							outdatedDependencies[moduleId] = [];
						addAllToSet(
							outdatedDependencies[moduleId],
							result.outdatedDependencies[moduleId]
						);
					}
				}
			}
			if (doDispose) {
				addAllToSet(outdatedModules, [result.moduleId]);
				appliedUpdate[moduleId] = warnUnexpectedRequire;
			}
		}
	}
	currentUpdate = undefined;

	var outdatedSelfAcceptedModules = [];
	for (var j = 0; j < outdatedModules.length; j++) {
		var outdatedModuleId = outdatedModules[j];
		var module = __webpack_require__.c[outdatedModuleId];
		if (
			module &&
			(module.hot._selfAccepted || module.hot._main) &&
			// removed self-accepted modules should not be required
			appliedUpdate[outdatedModuleId] !== warnUnexpectedRequire &&
			// when called invalidate self-accepting is not possible
			!module.hot._selfInvalidated
		) {
			outdatedSelfAcceptedModules.push({
				module: outdatedModuleId,
				require: module.hot._requireSelf,
				errorHandler: module.hot._selfAccepted
			});
		}
	} 

	var moduleOutdatedDependencies;
	return {
		dispose: function () {
			currentUpdateRemovedChunks.forEach(function (chunkId) {
				delete installedChunks[chunkId];
			});
			currentUpdateRemovedChunks = undefined;

			var idx;
			var queue = outdatedModules.slice();
			while (queue.length > 0) {
				var moduleId = queue.pop();
				var module = __webpack_require__.c[moduleId];
				if (!module) continue;

				var data = {};

				// Call dispose handlers
				var disposeHandlers = module.hot._disposeHandlers; 
				for (j = 0; j < disposeHandlers.length; j++) {
					disposeHandlers[j].call(null, data);
				}
				__webpack_require__.hmrD[moduleId] = data;

				module.hot.active = false;

				delete __webpack_require__.c[moduleId];

				delete outdatedDependencies[moduleId];

				for (j = 0; j < module.children.length; j++) {
					var child = __webpack_require__.c[module.children[j]];
					if (!child) continue;
					idx = child.parents.indexOf(moduleId);
					if (idx >= 0) {
						child.parents.splice(idx, 1);
					}
				}
			}

			var dependency;
			for (var outdatedModuleId in outdatedDependencies) {
				if (__webpack_require__.o(outdatedDependencies, outdatedModuleId)) {
					module = __webpack_require__.c[outdatedModuleId];
					if (module) {
						moduleOutdatedDependencies = outdatedDependencies[outdatedModuleId];
						for (j = 0; j < moduleOutdatedDependencies.length; j++) {
							dependency = moduleOutdatedDependencies[j];
							idx = module.children.indexOf(dependency);
							if (idx >= 0) module.children.splice(idx, 1);
						}
					}
				}
			}
		},
		apply: function (reportError) {
			// insert new code
			for (var updateModuleId in appliedUpdate) {
				if (__webpack_require__.o(appliedUpdate, updateModuleId)) {
					__webpack_require__.m[updateModuleId] = appliedUpdate[updateModuleId]; 
				}
			}

			// run new runtime modules
			for (var i = 0; i < currentUpdateRuntime.length; i++) {
				currentUpdateRuntime[i](__webpack_require__);
			}

			// call accept handlers
			for (var outdatedModuleId in outdatedDependencies) {
				if (__webpack_require__.o(outdatedDependencies, outdatedModuleId)) {
					var module = __webpack_require__.c[outdatedModuleId];
					if (module) {
						moduleOutdatedDependencies = outdatedDependencies[outdatedModuleId];
						var callbacks = [];
						var errorHandlers = [];
						var dependenciesForCallbacks = [];
						for (var j = 0; j < moduleOutdatedDependencies.length; j++) {
							var dependency = moduleOutdatedDependencies[j];
							var acceptCallback = module.hot._acceptedDependencies[dependency];
							var errorHandler = module.hot._acceptedErrorHandlers[dependency];
							if (acceptCallback) {
								if (callbacks.indexOf(acceptCallback) !== -1) continue;
								callbacks.push(acceptCallback);
								errorHandlers.push(errorHandler); 
								dependenciesForCallbacks.push(dependency);
							}
						}
						for (var k = 0; k < callbacks.length; k++) {
							try {
								callbacks[k].call(null, moduleOutdatedDependencies);
							} catch (err) {
								if (typeof errorHandlers[k] === "function") {
									try {
										errorHandlers[k](err, {
											moduleId: outdatedModuleId,
											dependencyId: dependenciesForCallbacks[k]
										});
									} catch (err2) {
										if (options.onErrored) {
											options.onErrored({
												type: "accept-error-handler-errored",
												moduleId: outdatedModuleId,
												dependencyId: dependenciesForCallbacks[k],
												error: err2,
												originalError: err
											});
										}
										if (!options.ignoreErrored) {
											reportError(err2);
											reportError(err);
										}
									}
								} else {
									if (options.onErrored) {
										options.onErrored({
											type: "accept-errored",
											moduleId: outdatedModuleId,
											dependencyId: dependenciesForCallbacks[k],
											error: err
										});
									}
									if (!options.ignoreErrored) {
										reportError(err);
									}
								}
							}
						}
					}
				}
			}

			// Load self accepted modules
			for (var o = 0; o < outdatedSelfAcceptedModules.length; o++) {
				var item = outdatedSelfAcceptedModules[o];
				var moduleId = item.module;
				try {
					item.require(moduleId);
				} catch (err) {
					if (typeof item.errorHandler === "function") {
						try {
							item.errorHandler(err, {
								moduleId: moduleId,
								module: __webpack_require__.c[moduleId]
							});
						} catch (err1) {
							if (options.onErrored) {
								options.onErrored({
									type: "self-accept-error-handler-errored",
									moduleId: moduleId,
									error: err1,
									originalError: err
								});
							}
							if (!options.ignoreErrored) {
								reportError(err1);
								reportError(err);
							}
						}
					} else {
						if (options.onErrored) {
							options.onErrored({
								type: "self-accept-errored",
								moduleId: moduleId,
								error: err
							});
						}
						if (!options.ignoreErrored) {
							reportError(err);
						}
					}
				}
			}

			return outdatedModules;
		}
	};
}

__webpack_require__.hmrI.jsonp = function (moduleId, applyHandlers) {
	if (!currentUpdate) {
		currentUpdate = {};
		currentUpdateRuntime = [];
		currentUpdateRemovedChunks = [];
		applyHandlers.push(applyHandler);
	}
	if (!__webpack_require__.o(currentUpdate, moduleId)) {
		currentUpdate[moduleId] = __webpack_require__.m[moduleId];
	}
};

__webpack_require__.hmrC.jsonp = function (
	chunkIds,
	removedChunks,
	removedModules,
	promises,
	applyHandlers,
	updatedModulesList
) {
	applyHandlers.push(applyHandler);
	currentUpdateChunks = {};
	currentUpdateRemovedChunks = removedChunks;
	currentUpdate = removedModules.reduce(function (obj, key) {
		obj[key] = false;
		return obj;
	}, {});
	currentUpdateRuntime = [];
	chunkIds.forEach(function (chunkId) {
		if (
			__webpack_require__.o(installedChunks, chunkId) &&
			installedChunks[chunkId] !== undefined
		) {
			promises.push(loadUpdateChunk(chunkId, updatedModulesList));
			currentUpdateChunks[chunkId] = true;
		} else {
			currentUpdateChunks[chunkId] = false;
		}
	});
	if (__webpack_require__.f) {
		__webpack_require__.f.jsonpHmr = function (chunkId, promises) {
			if (
				currentUpdateChunks &&
				__webpack_require__.o(currentUpdateChunks, chunkId) &&
				!currentUpdateChunks[chunkId]
			) {
				promises.push(loadUpdateChunk(chunkId));
				currentUpdateChunks[chunkId] = true;
			}
		};
	}
};
__webpack_require__.hmrM = () => {
	if (typeof fetch === "undefined")
		throw new Error("No browser support: need fetch API");
	return fetch(__webpack_require__.p + __webpack_require__.hmrF()).then(
		(response) => {
			if (response.status === 404) return; // no update available
			if (!response.ok)
				throw new Error(
					"Failed to fetch update manifest " + response.statusText
				);
			return response.json();
		}
	);
};
__webpack_require__.O.j = (chunkId) => (installedChunks[chunkId] === 0);
// install a JSONP callback for chunk loading
var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
	var [chunkIds, moreModules, runtime] = data;
	// add "moreModules" to the modules object,
	// then flag all "chunkIds" as loaded and fire callback
	var moduleId, chunkId, i = 0;
	if (chunkIds.some((id) => (installedChunks[id] !== 0))) {
		for (moduleId in moreModules) {
			if (__webpack_require__.o(moreModules, moduleId)) {
				__webpack_require__.m[moduleId] = moreModules[moduleId];
			}
		}
		if (runtime) var result = runtime(__webpack_require__);
	}
	if (parentChunkLoadingFunction) parentChunkLoadingFunction(data);
	for (; i < chunkIds.length; i++) {
		chunkId = chunkIds[i];
		if (
			__webpack_require__.o(installedChunks, chunkId) &&
			installedChunks[chunkId]
		) {
			installedChunks[chunkId][0]();
		}
		installedChunks[chunkId] = 0;
	}
	return __webpack_require__.O(result);
};

var chunkLoadingGlobal = self["webpackChunkdiva_js"] = self["webpackChunkdiva_js"] || [];
chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
chunkLoadingGlobal.push = webpackJsonpCallback.bind(
	null,
	chunkLoadingGlobal.push.bind(chunkLoadingGlobal)
);

})();
// webpack/runtime/rspack_unique_id
(() => {
__webpack_require__.ruid = "bundler=rspack@1.2.8";

})();
/************************************************************************/
// module cache are used so entry inlining is disabled
// startup
// Load entry module and return exports
__webpack_require__.O(undefined, ["vendors-node_modules_rspack_core_dist_cssExtractHmr_js-node_modules_debug_src_browser_js-node-db2334"], function() { return __webpack_require__("./source/js/diva.ts") });
var __webpack_exports__ = __webpack_require__.O(undefined, ["vendors-node_modules_rspack_core_dist_cssExtractHmr_js-node_modules_debug_src_browser_js-node-db2334"], function() { return __webpack_require__("./source/css/diva.scss") });
__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
})()
;
//# sourceMappingURL=diva.js.map