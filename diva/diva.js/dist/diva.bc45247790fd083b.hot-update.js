"use strict";
self["webpackHotUpdatediva_js"]('diva', {
"./source/js/image-manifest.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
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

},function(__webpack_require__) {
// webpack/runtime/get_full_hash
(() => {
__webpack_require__.h = () => ("c20812433176aed8")
})();

}
);
//# sourceMappingURL=diva.bc45247790fd083b.hot-update.js.map