"use strict";
self["webpackHotUpdatediva_js"]('diva', {
"./source/js/viewer-core.ts": (function (__unused_webpack_module, __webpack_exports__, __webpack_require__) {
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

},function(__webpack_require__) {
// webpack/runtime/get_full_hash
(() => {
__webpack_require__.h = () => ("9055bbc6c0f8e939")
})();

}
);
//# sourceMappingURL=diva.29e2f11fff01ce91.hot-update.js.map