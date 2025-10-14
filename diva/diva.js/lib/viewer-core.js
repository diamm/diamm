import { elt } from './utils/elt';
import getScrollbarWidth from './utils/get-scrollbar-width';
import gestureEvents from './gesture-events';
import globalDiva from './diva-global';
import DocumentHandler from './document-handler';
import GridHandler from './grid-handler';
import PageOverlayManager from './page-overlay-manager';
import Renderer from './renderer';
import getPageLayouts from './page-layouts';
import ValidationRunner from './validation-runner';
import Viewport from './viewport';
const debug = require('debug')('diva:ViewerCore');
function generateId() {
    return generateId.counter++;
}
generateId.counter = 1;
function createSettingsView(sources) {
    const obj = {};
    sources.forEach((source) => {
        registerMixin(obj, source);
    });
    return obj;
}
function registerMixin(obj, mixin) {
    Object.keys(mixin).forEach((key) => {
        Object.defineProperty(obj, key, {
            get: () => {
                return mixin[key];
            },
            set: () => {
                throw new TypeError('Cannot set settings.' + key);
            }
        });
    });
}
function arraysEqual(a, b) {
    if (a.length !== b.length)
        return false;
    for (let i = 0, len = a.length; i < len; i++) {
        if (a[i] !== b[i])
            return false;
    }
    return true;
}
const optionsValidations = [
    {
        key: 'goDirectlyTo',
        validate: (value, settings) => {
            if (value < 0 || value >= settings.manifest.pages.length)
                return 0;
        }
    },
    {
        key: 'minPagesPerRow',
        validate: (value) => {
            return Math.max(2, value);
        }
    },
    {
        key: 'maxPagesPerRow',
        validate: (value, settings) => {
            return Math.max(value, settings.minPagesPerRow);
        }
    },
    {
        key: 'pagesPerRow',
        validate: (value, settings) => {
            if (value < settings.minPagesPerRow || value > settings.maxPagesPerRow)
                return settings.maxPagesPerRow;
        }
    },
    {
        key: 'maxZoomLevel',
        validate: (value, settings, config) => {
            config.suppressWarning();
            if (value < 0 || value > settings.manifest.maxZoom)
                return settings.manifest.maxZoom;
        }
    },
    {
        key: 'minZoomLevel',
        validate: (value, settings, config) => {
            if (value > settings.manifest.maxZoom) {
                config.suppressWarning();
                return 0;
            }
            if (value < 0 || value > settings.maxZoomLevel)
                return 0;
        }
    },
    {
        key: 'zoomLevel',
        validate: (value, settings, config) => {
            if (value > settings.manifest.maxZoom) {
                config.suppressWarning();
                return 0;
            }
            if (value < settings.minZoomLevel || value > settings.maxZoomLevel)
                return settings.minZoomLevel;
        }
    }
];
export default class ViewerCore {
    constructor(element, options, publicInstance) {
        this.parentObject = element;
        this.publicInstance = publicInstance;
        this.viewerState = {
            currentPageIndices: [0],
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
            pageOverlays: new PageOverlayManager(),
            pageTools: [],
            parentObject: this.parentObject,
            pendingManifestRequest: null,
            pluginInstances: [],
            renderer: null,
            resizeTimer: -1,
            scrollbarWidth: 0,
            selector: '',
            throbberTimeoutID: -1,
            toolbar: null,
            verticalOffset: 0,
            verticalPadding: 0,
            viewHandler: null,
            viewport: null,
            viewportElement: null,
            viewportObject: null,
            zoomDuration: 400
        };
        this.settings = createSettingsView([options, this.viewerState]);
        const idNumber = generateId();
        this.viewerState.ID = 'diva-' + idNumber + '-';
        this.viewerState.selector = this.settings.ID;
        Object.defineProperties(this.settings, {
            panelHeight: {
                get: () => {
                    return this.viewerState.viewport.height;
                }
            },
            panelWidth: {
                get: () => {
                    return this.viewerState.viewport.width;
                }
            }
        });
        this.optionsValidator = new ValidationRunner({
            additionalProperties: [
                {
                    key: 'manifest',
                    get: () => {
                        return this.viewerState.manifest;
                    }
                }
            ],
            validations: optionsValidations
        });
        this.viewerState.scrollbarWidth = getScrollbarWidth();
        this.viewerState.mobileWebkit = window.screen.orientation !== undefined;
        if (options.hashParamSuffix === null) {
            if (idNumber === 1)
                options.hashParamSuffix = '';
            else
                options.hashParamSuffix = idNumber + '';
        }
        const innerElem = elt('div', this.elemAttrs('inner', { class: 'diva-inner' }));
        const viewportElem = elt('div', this.elemAttrs('viewport'), innerElem);
        const outerElem = elt('div', this.elemAttrs('outer'), viewportElem, elt('div', this.elemAttrs('throbber'), [
            elt('div', { class: 'cube cube1' }),
            elt('div', { class: 'cube cube2' }),
            elt('div', { class: 'cube cube3' }),
            elt('div', { class: 'cube cube4' }),
            elt('div', { class: 'cube cube5' }),
            elt('div', { class: 'cube cube6' }),
            elt('div', { class: 'cube cube7' }),
            elt('div', { class: 'cube cube8' }),
            elt('div', { class: 'cube cube9' }),
        ]));
        this.viewerState.innerElement = innerElem;
        this.viewerState.viewportElement = viewportElem;
        this.viewerState.outerElement = outerElem;
        this.viewerState.innerObject = innerElem;
        this.viewerState.viewportObject = viewportElem;
        this.viewerState.outerObject = outerElem;
        this.settings.parentObject.append(outerElem);
        this.viewerState.viewport = new Viewport(this.viewerState.viewportElement, {
            intersectionTolerance: this.settings.viewportMargin
        });
        this.boundScrollFunction = this.scrollFunction.bind(this);
        this.boundEscapeListener = this.escapeListener.bind(this);
        this.initPlugins();
        this.handleEvents();
        this.showThrobber();
    }
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
        }
        else {
            return attrs;
        }
    }
    getPageData(pageIndex, attribute) {
        return this.settings.manifest.pages[pageIndex].d[this.settings.zoomLevel][attribute];
    }
    clearViewer() {
        this.viewerState.viewport.top = 0;
        clearTimeout(this.viewerState.resizeTimer);
    }
    hasChangedOption(options, key) {
        return key in options && options[key] !== this.settings[key];
    }
    escapeListener(e) {
        if (e.code === 'Escape') {
            this.publicInstance.leaveFullscreenMode();
        }
    }
    reloadViewer(newOptions) {
        const queuedEvents = [];
        newOptions = this.optionsValidator.getValidatedOptions(this.settings, newOptions);
        if (this.hasChangedOption(newOptions, 'zoomLevel')) {
            this.viewerState.oldZoomLevel = this.settings.zoomLevel;
            this.viewerState.options.zoomLevel = newOptions.zoomLevel;
            queuedEvents.push(["ZoomLevelDidChange", newOptions.zoomLevel]);
        }
        if (this.hasChangedOption(newOptions, 'pagesPerRow')) {
            this.viewerState.options.pagesPerRow = newOptions.pagesPerRow;
            queuedEvents.push(["GridRowNumberDidChange", newOptions.pagesPerRow]);
        }
        if (this.hasChangedOption(newOptions, 'verticallyOriented'))
            this.viewerState.options.verticallyOriented = newOptions.verticallyOriented;
        if (this.hasChangedOption(newOptions, 'showNonPagedPages')) {
            this.viewerState.options.showNonPagedPages = newOptions.showNonPagedPages;
        }
        if ('goDirectlyTo' in newOptions) {
            this.viewerState.options.goDirectlyTo = newOptions.goDirectlyTo;
            if ('verticalOffset' in newOptions) {
                this.viewerState.verticalOffset = newOptions.verticalOffset;
            }
            if ('horizontalOffset' in newOptions) {
                this.viewerState.horizontalOffset = newOptions.horizontalOffset;
            }
        }
        else {
            this.viewerState.options.goDirectlyTo = this.settings.activePageIndex;
        }
        if (this.hasChangedOption(newOptions, 'inGrid') || this.hasChangedOption(newOptions, 'inBookLayout')) {
            if ('inGrid' in newOptions) {
                this.viewerState.options.inGrid = newOptions.inGrid;
            }
            if ('inBookLayout' in newOptions) {
                this.viewerState.options.inBookLayout = newOptions.inBookLayout;
            }
            queuedEvents.push(["ViewDidSwitch", this.settings.inGrid]);
        }
        if (this.hasChangedOption(newOptions, 'inFullscreen')) {
            this.viewerState.options.inFullscreen = newOptions.inFullscreen;
            this.prepareModeChange(newOptions);
            queuedEvents.push(["ModeDidSwitch", this.settings.inFullscreen]);
        }
        this.clearViewer();
        this.updateViewHandlerAndRendering();
        if (this.viewerState.renderer) {
            const rendererConfig = {
                pageLayouts: getPageLayouts(this.settings),
                padding: this.getPadding(),
                maxZoomLevel: this.settings.inGrid ? null : this.viewerState.manifest.maxZoom,
                verticallyOriented: this.settings.verticallyOriented || this.settings.inGrid,
            };
            const viewportPosition = {
                zoomLevel: this.settings.inGrid ? null : this.settings.zoomLevel,
                anchorPage: this.settings.goDirectlyTo,
                verticalOffset: this.viewerState.verticalOffset,
                horizontalOffset: this.viewerState.horizontalOffset
            };
            const sourceProvider = this.getCurrentSourceProvider();
            if (debug.enabled) {
                const serialized = Object.keys(rendererConfig)
                    .filter(function (key) {
                    return key !== 'pageLayouts' && key !== 'padding';
                })
                    .map(function (key) {
                    const value = rendererConfig[key];
                    return key + ': ' + JSON.stringify(value);
                })
                    .join(', ');
                debug('reload with %s', serialized);
            }
            this.viewerState.renderer.load(rendererConfig, viewportPosition, sourceProvider);
        }
        queuedEvents.forEach((params) => {
            this.publish.apply(this, params);
        });
        return true;
    }
    prepareModeChange(options) {
        const changeClass = options.inFullscreen ? 'add' : 'remove';
        this.viewerState.outerObject.classList[changeClass]('diva-fullscreen');
        document.body.classList[changeClass]('diva-hide-scrollbar');
        this.settings.parentObject.classList[changeClass]('diva-full-width');
        const storedHeight = this.settings.panelHeight;
        const storedWidth = this.settings.panelWidth;
        this.viewerState.viewport.invalidate();
        if (!this.viewerState.loaded && !this.settings.inGrid && !('verticalOffset' in options)) {
            const newHeight = this.settings.panelHeight;
            const newWidth = this.settings.panelWidth;
            this.viewerState.verticalOffset += ((storedHeight - newHeight) / 2);
            this.viewerState.horizontalOffset += ((storedWidth - newWidth) / 2);
        }
        if (options.inFullscreen)
            document.addEventListener('keyup', this.boundEscapeListener);
        else
            document.removeEventListener('keyup', this.boundEscapeListener);
    }
    updateViewHandlerAndRendering() {
        const Handler = this.settings.inGrid ? GridHandler : DocumentHandler;
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
    initializeRenderer() {
        const compatErrors = Renderer.getCompatibilityErrors();
        if (compatErrors) {
            this.showError(compatErrors);
        }
        else {
            const options = {
                viewport: this.viewerState.viewport,
                outerElement: this.viewerState.outerElement,
                innerElement: this.viewerState.innerElement,
                settings: this.settings
            };
            const hooks = {
                onViewWillLoad: () => {
                    this.viewerState.viewHandler.onViewWillLoad();
                },
                onViewDidLoad: () => {
                    this.updatePageOverlays();
                    this.viewerState.viewHandler.onViewDidLoad();
                },
                onViewDidUpdate: (pages, targetPage) => {
                    this.updatePageOverlays();
                    this.viewerState.viewHandler.onViewDidUpdate(pages, targetPage);
                },
                onViewDidTransition: () => {
                    this.updatePageOverlays();
                },
                onPageWillLoad: (pageIndex) => {
                    this.publish('PageWillLoad', pageIndex);
                },
                onZoomLevelWillChange: (zoomLevel) => {
                    this.publish('ZoomLevelWillChange', zoomLevel);
                }
            };
            this.viewerState.renderer = new Renderer(options, hooks);
        }
    }
    getCurrentSourceProvider() {
        if (this.settings.inGrid) {
            const gridSourceProvider = {
                getAllZoomLevelsForPage: (page) => {
                    return [gridSourceProvider.getBestZoomLevelForPage(page)];
                },
                getBestZoomLevelForPage: (page) => {
                    const url = this.settings.manifest.getPageImageURL(page.index, {
                        width: page.dimensions.width
                    });
                    return {
                        zoomLevel: 1,
                        rows: 1,
                        cols: 1,
                        tiles: [{
                                url: url,
                                zoomLevel: 1,
                                row: 0,
                                col: 0,
                                dimensions: page.dimensions,
                                offset: {
                                    top: 0,
                                    left: 0
                                }
                            }]
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
            getBestZoomLevelForPage: (page) => {
                return this.settings.manifest.getPageImageTiles(page.index, Math.ceil(this.settings.zoomLevel), tileDimensions);
            },
            getAllZoomLevelsForPage: (page) => {
                const levels = [];
                const levelCount = this.viewerState.manifest.maxZoom;
                for (let level = 0; level <= levelCount; level++) {
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
        }
        else {
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
    handleZoom(newZoomLevel, focalPoint) {
        if (!this.isValidOption('zoomLevel', newZoomLevel))
            return false;
        this.viewerState.viewportObject.removeEventListener('scroll', this.boundScrollFunction);
        if (!focalPoint) {
            const viewport = this.viewerState.viewport;
            const currentRegion = this.viewerState.renderer.layout.getPageRegion(this.settings.activePageIndex);
            focalPoint = {
                anchorPage: this.settings.activePageIndex,
                offset: {
                    left: (viewport.width / 2) - (currentRegion.left - viewport.left),
                    top: (viewport.height / 2) - (currentRegion.top - viewport.top)
                }
            };
        }
        const pageRegion = this.viewerState.renderer.layout.getPageRegion(focalPoint.anchorPage);
        const focalXToCenter = (pageRegion.left + focalPoint.offset.left) -
            (this.settings.viewport.left + (this.settings.viewport.width / 2));
        const focalYToCenter = (pageRegion.top + focalPoint.offset.top) -
            (this.settings.viewport.top + (this.settings.viewport.height / 2));
        const getPositionForZoomLevel = (zoomLevel, initZoom) => {
            const zoomRatio = Math.pow(2, zoomLevel - initZoom);
            const horizontalOffset = (focalPoint.offset.left * zoomRatio) - focalXToCenter;
            const verticalOffset = (focalPoint.offset.top * zoomRatio) - focalYToCenter;
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
            getPosition: (parameters) => {
                return getPositionForZoomLevel(parameters.zoomLevel, initialZoomLevel);
            },
            onEnd: (info) => {
                this.viewerState.viewportObject.addEventListener('scroll', this.boundScrollFunction);
                if (info.interrupted)
                    this.viewerState.oldZoomLevel = newZoomLevel;
            }
        });
        let zoomInButton = document.getElementById(this.settings.selector + 'zoom-in-button');
        let zoomOutButton = document.getElementById(this.settings.selector + 'zoom-out-button');
        zoomInButton.disabled = true;
        zoomOutButton.disabled = true;
        setTimeout(() => {
            zoomInButton.disabled = false;
            zoomOutButton.disabled = false;
        }, this.settings.zoomDuration);
        this.publish("ZoomLevelDidChange", newZoomLevel);
        return true;
    }
    getYOffset(pageIndex, anchor) {
        let pidx = (typeof (pageIndex) === "undefined" ? this.settings.activePageIndex : pageIndex);
        if (anchor === "center" || anchor === "centre") {
            return parseInt(this.getPageData(pidx, "h") / 2, 10);
        }
        else if (anchor === "bottom") {
            return parseInt(this.getPageData(pidx, "h") - this.settings.panelHeight / 2, 10);
        }
        else {
            return parseInt(this.settings.panelHeight / 2, 10);
        }
    }
    getXOffset(pageIndex, anchor) {
        let pidx = (typeof (pageIndex) === "undefined" ? this.settings.activePageIndex : pageIndex);
        if (anchor === "left") {
            return parseInt(this.settings.panelWidth / 2, 10);
        }
        else if (anchor === "right") {
            return parseInt(this.getPageData(pidx, "w") - this.settings.panelWidth / 2, 10);
        }
        else {
            return parseInt(this.getPageData(pidx, "w") / 2, 10);
        }
    }
    updatePanelSize() {
        this.viewerState.viewport.invalidate();
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
    bindMouseEvents() {
        this.viewerState.viewportObject.classList.add('dragscroll');
        gestureEvents.onDoubleClick(this.viewerState.viewportObject, (event, coords) => {
            debug('Double click at %s, %s', coords.left, coords.top);
            this.viewerState.viewHandler.onDoubleClick(event, coords);
        });
    }
    onResize() {
        this.updatePanelSize();
        clearTimeout(this.viewerState.resizeTimer);
        this.viewerState.resizeTimer = setTimeout(() => {
            const pageOffset = this.viewerState.renderer.layout.getPageToViewportCenterOffset(this.settings.activePageIndex, this.viewerState.viewport);
            if (pageOffset) {
                this.reloadViewer({
                    goDirectlyTo: this.settings.activePageIndex,
                    verticalOffset: pageOffset.y,
                    horizontalOffset: pageOffset.x
                });
            }
            else {
                this.reloadViewer({
                    goDirectlyTo: this.settings.activePageIndex
                });
            }
        }, 200);
    }
    bindTouchEvents() {
        if (this.settings.blockMobileMove) {
            document.body.addEventListener('touchmove', (event) => {
                const e = event.originalEvent;
                e.preventDefault();
                return false;
            });
        }
        gestureEvents.onPinch(this.viewerState.viewportObject, (event, coords, start, end) => {
            debug('Pinch %s at %s, %s', end - start, coords.left, coords.top);
            this.viewerState.viewHandler.onPinch(event, coords, start, end);
        });
        gestureEvents.onDoubleTap(this.viewerState.viewportObject, (event, coords) => {
            debug('Double tap at %s, %s', coords.left, coords.top);
            this.viewerState.viewHandler.onDoubleClick(event, coords);
        });
    }
    scrollFunction() {
        const previousTopScroll = this.viewerState.viewport.top;
        const previousLeftScroll = this.viewerState.viewport.left;
        let direction;
        this.viewerState.viewport.invalidate();
        const newScrollTop = this.viewerState.viewport.top;
        const newScrollLeft = this.viewerState.viewport.left;
        if (this.settings.verticallyOriented || this.settings.inGrid) {
            direction = newScrollTop - previousTopScroll;
        }
        else {
            direction = newScrollLeft - previousLeftScroll;
        }
        this.viewerState.renderer.adjust();
        const primaryScroll = (this.settings.verticallyOriented || this.settings.inGrid) ? newScrollTop : newScrollLeft;
        this.publish("ViewerDidScroll", primaryScroll);
        if (direction > 0) {
            this.publish("ViewerDidScrollDown", primaryScroll);
        }
        else if (direction < 0) {
            this.publish("ViewerDidScrollUp", primaryScroll);
        }
        this.updateOffsets();
    }
    handleEvents() {
        this.viewerState.innerObject.addEventListener('mousedown', () => {
            this.viewerState.innerObject.classList.add('diva-grabbing');
        });
        this.viewerState.innerObject.addEventListener('mouseup', () => {
            this.viewerState.innerObject.classList.remove('diva-grabbing');
        });
        this.bindMouseEvents();
        this.viewerState.viewportObject.addEventListener('scroll', this.boundScrollFunction);
        const upArrowKey = 38, downArrowKey = 40, leftArrowKey = 37, rightArrowKey = 39, spaceKey = 32, pageUpKey = 33, pageDownKey = 34, homeKey = 36, endKey = 35;
        document.addEventListener('keydown.diva', (event) => {
            if (!this.viewerState.isActiveDiva)
                return true;
            if ((this.settings.enableSpaceScroll && !event.shiftKey && event.keyCode === spaceKey) || (this.settings.enableKeyScroll && event.keyCode === pageDownKey)) {
                this.viewerState.viewport.top += this.settings.panelHeight;
                return false;
            }
            else if (!this.settings.enableSpaceScroll && event.keyCode === spaceKey) {
                event.preventDefault();
            }
            if (this.settings.enableKeyScroll) {
                if (event.shiftKey || event.ctrlKey || event.metaKey)
                    return true;
                switch (event.keyCode) {
                    case pageUpKey:
                        this.viewerState.viewport.top -= this.settings.panelHeight;
                        return false;
                    case upArrowKey:
                        this.viewerState.viewport.top -= this.settings.arrowScrollAmount;
                        return false;
                    case downArrowKey:
                        this.viewerState.viewport.top += this.settings.arrowScrollAmount;
                        return false;
                    case leftArrowKey:
                        this.viewerState.viewport.left -= this.settings.arrowScrollAmount;
                        return false;
                    case rightArrowKey:
                        this.viewerState.viewport.left += this.settings.arrowScrollAmount;
                        return false;
                    case homeKey:
                        this.viewerState.viewport.top = 0;
                        return false;
                    case endKey:
                        if (this.settings.verticallyOriented)
                            this.viewerState.viewport.top = Infinity;
                        else
                            this.viewerState.viewport.left = Infinity;
                        return false;
                    default:
                        return true;
                }
            }
            return true;
        });
        diva.Events.subscribe('ViewerDidTerminate', function () {
            document.removeEventListener('keydown.diva');
        }, this.settings.ID);
        window.addEventListener('resize', this.onResize.bind(this), false);
        diva.Events.subscribe('ViewerDidTerminate', function () {
            window.removeEventListener('resize', this.onResize, false);
        }, this.settings.ID);
        if ('onorientationchange' in window) {
            window.addEventListener('orientationchange', this.onResize, false);
            diva.Events.subscribe('ViewerDidTerminate', function () {
                window.removeEventListener('orientationchange', this.onResize, false);
            }, this.settings.ID);
        }
        diva.Events.subscribe('PanelSizeDidChange', this.updatePanelSize, this.settings.ID);
        diva.Events.subscribe('ViewerDidTerminate', () => {
            if (this.viewerState.renderer)
                this.viewerState.renderer.destroy();
            clearTimeout(this.viewerState.resizeTimer);
        }, this.settings.ID);
    }
    initPlugins() {
        if (!this.settings.hasOwnProperty('plugins'))
            return null;
        this.viewerState.pluginInstances = this.settings.plugins.map((plugin) => {
            const p = new plugin(this);
            if (p.isPageTool)
                this.viewerState.pageTools.push(p);
            return p;
        });
    }
    showThrobber() {
        this.hideThrobber();
        this.viewerState.throbberTimeoutID = setTimeout(() => {
            let thb = document.getElementById(this.settings.selector + 'throbber');
            if (thb)
                thb.style.display = 'block';
        }, this.settings.throbberTimeout);
    }
    hideThrobber() {
        clearTimeout(this.viewerState.throbberTimeoutID);
        let thb = document.getElementById(this.settings.selector + 'throbber');
        if (thb)
            thb.style.display = 'none';
    }
    showError(message) {
        const errorElement = elt('div', this.elemAttrs('error'), [
            elt('button', this.elemAttrs('error-close', { 'aria-label': 'Close dialog' })),
            elt('p', elt('strong', 'Error')),
            elt('div', message)
        ]);
        this.viewerState.outerObject.appendChild(errorElement);
        document.getElementById(this.settings.selector + 'error-close').addEventListener('click', () => {
            errorElement.parentNode.removeChild(errorElement);
        });
    }
    setManifest(manifest, loadOptions) {
        this.viewerState.manifest = manifest;
        this.hideThrobber();
        this.viewerState.numPages = this.settings.manifest.pages.length;
        this.optionsValidator.validate(this.viewerState.options);
        this.publish('NumberOfPagesDidChange', this.settings.numPages);
        if (this.settings.adaptivePadding > 0) {
            const z = Math.floor((this.settings.minZoomLevel + this.settings.maxZoomLevel) / 2);
            this.viewerState.horizontalPadding = parseInt(this.settings.manifest.getAverageWidth(z) * this.settings.adaptivePadding, 10);
            this.viewerState.verticalPadding = parseInt(this.settings.manifest.getAverageHeight(z) * this.settings.adaptivePadding, 10);
        }
        else {
            this.viewerState.horizontalPadding = this.settings.fixedPadding;
            this.viewerState.verticalPadding = this.settings.fixedPadding;
        }
        if (this.viewerState.pageTools.length) {
            this.viewerState.verticalPadding = Math.max(40, this.viewerState.verticalPadding);
        }
        if (this.settings.manifest.paged) {
            this.viewerState.options.inBookLayout = true;
        }
        this.publish('ObjectDidLoad', this.settings);
        this.updatePanelSize();
        let needsXCoord, needsYCoord;
        let anchoredVertically = false;
        let anchoredHorizontally = false;
        if (loadOptions.goDirectlyTo == null) {
            loadOptions.goDirectlyTo = this.settings.goDirectlyTo;
            needsXCoord = needsYCoord = true;
        }
        else {
            needsXCoord = loadOptions.horizontalOffset == null || isNaN(loadOptions.horizontalOffset);
            needsYCoord = loadOptions.verticalOffset == null || isNaN(loadOptions.verticalOffset);
        }
        if (needsXCoord) {
            if (loadOptions.goDirectlyTo === 0 && this.settings.inBookLayout && this.settings.verticallyOriented) {
                loadOptions.horizontalOffset = this.viewerState.horizontalPadding;
            }
            else {
                anchoredHorizontally = true;
                loadOptions.horizontalOffset = this.getXOffset(loadOptions.goDirectlyTo, "center");
            }
        }
        if (needsYCoord) {
            anchoredVertically = true;
            loadOptions.verticalOffset = this.getYOffset(loadOptions.goDirectlyTo, "top");
        }
        this.reloadViewer(loadOptions);
        this.updatePanelSize();
        if (this.settings.enableAutoTitle) {
            let title = document.getElementById(this.settings.selector + 'title');
            if (title) {
                title.innerHTML = this.settings.manifest.itemTitle;
            }
            else {
                this.settings.parentObject.insertBefore(elt('div', this.elemAttrs('title'), [this.settings.manifest.itemTitle]), this.settings.parentObject.firstChild);
            }
        }
        if (this.settings.verticallyOriented)
            this.viewerState.innerElement.style.minWidth = this.settings.panelWidth + 'px';
        else
            this.viewerState.innerElement.style.minHeight = this.settings.panelHeight + 'px';
        if (anchoredVertically || anchoredHorizontally) {
            if (anchoredVertically)
                this.viewerState.verticalOffset = this.getYOffset(this.settings.activePageIndex, "top");
            if (anchoredHorizontally)
                this.viewerState.horizontalOffset = this.getXOffset(this.settings.activePageIndex, "center");
            this.viewerState.renderer.goto(this.settings.activePageIndex, this.viewerState.verticalOffset, this.viewerState.horizontalOffset);
        }
        this.viewerState.loaded = true;
        this.publish("ViewerDidLoad", this.settings);
    }
    publish(event) {
        const args = Array.prototype.slice.call(arguments, 1);
        globalDiva.Events.publish(event, args, this.publicInstance);
    }
    getSettings() {
        return this.settings;
    }
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
    getViewport() {
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
                }
                else {
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
        const renderedPages = this.viewerState.renderer.getRenderedPages();
        const pageCount = renderedPages.length;
        for (let i = 0; i < pageCount; i++) {
            const pageIndex = renderedPages[i];
            const region = this.viewerState.renderer.layout.getPageRegion(pageIndex);
            if (region.left <= docCoords.left && region.right >= docCoords.left &&
                region.top <= docCoords.top && region.bottom >= docCoords.top) {
                return {
                    anchorPage: pageIndex,
                    offset: {
                        left: docCoords.left - region.left,
                        top: docCoords.top - region.top
                    }
                };
            }
        }
        const currentRegion = this.viewerState.renderer.layout.getPageRegion(this.settings.activePageIndex);
        return {
            anchorPage: this.settings.activePageIndex,
            offset: {
                left: docCoords.left - currentRegion.left,
                top: docCoords.top - currentRegion.top
            }
        };
    }
    setCurrentPages(activePage, visiblePages) {
        if (!arraysEqual(this.viewerState.currentPageIndices, visiblePages)) {
            this.viewerState.currentPageIndices = visiblePages;
            if (this.viewerState.activePageIndex !== activePage) {
                this.viewerState.activePageIndex = activePage;
                this.publish("ActivePageDidChange", activePage);
            }
            this.publish("VisiblePageDidChange", visiblePages);
            if (this.viewerState.manifest.pages[activePage].otherImages.length > 0)
                this.publish('VisiblePageHasAlternateViews', activePage);
        }
        else if (this.viewerState.activePageIndex !== activePage) {
            this.viewerState.activePageIndex = activePage;
            this.publish("ActivePageDidChange", activePage);
        }
    }
    getPageName(pageIndex) {
        return this.viewerState.manifest.pages[pageIndex].f;
    }
    reload(newOptions) {
        this.reloadViewer(newOptions);
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
            this.disableDragScrollable();
            this.viewerState.outerObject.ondblclick = null;
            this.viewerState.outerObject.oncontextmenu = null;
            this.viewerState.viewportElement.style.overflow = 'hidden';
            this.viewerState.initialKeyScroll = this.settings.enableKeyScroll;
            this.viewerState.initialSpaceScroll = this.settings.enableSpaceScroll;
            this.viewerState.options.enableKeyScroll = false;
            this.viewerState.options.enableSpaceScroll = false;
            this.viewerState.isScrollable = false;
        }
    }
    disableDragScrollable() {
        if (!this.viewerState.viewportObject.hasAttribute('nochilddrag'))
            this.viewerState.viewportObject.setAttribute('nochilddrag', "");
    }
    clear() {
        this.clearViewer();
    }
    setPendingManifestRequest(pendingManifestRequest) {
        this.viewerState.pendingManifestRequest = pendingManifestRequest;
    }
    destroy() {
        this.publish('ViewerWillTerminate', this.settings);
        if (this.settings.pendingManifestRequest) {
            this.settings.pendingManifestRequest.abort();
        }
        document.body.classList.remove('diva-hide-scrollbar');
        this.settings.parentObject.parentElement.replaceChildren();
        this.settings.parentObject.parentElement.removeAttribute('style');
        this.settings.parentObject.parentElement.removeAttribute('class');
        this.publish('ViewerDidTerminate', this.settings);
        globalDiva.Events.unsubscribeAll(this.settings.ID);
    }
}
//# sourceMappingURL=viewer-core.js.map