import ImageManifest from "./image-manifest";
import PageOverlayManager from "./page-overlay-manager";
import Renderer from "./renderer";
import {LayoutGroupPages, PaddingDefinitions} from "./viewer-type-definitions";
import ViewerCore from "./viewer-core";

export type Options = {
    objectData: object | string // A IIIF Manifest or a URL pointing to such data - *REQUIRED*
    adaptivePadding: number,      // The ratio of padding to the page dimension
    arrowScrollAmount: number,      // The amount (in pixels) to scroll by when using arrow keys
    blockMobileMove: boolean,     // Prevent moving or scrolling the page on mobile devices
    enableAutoTitle: boolean,      // Shows the title within a div of id diva-title
    enableFilename: boolean,       // Uses filenames and not page numbers for links (i=bm_001.tif, not p=1)
    enableFullscreen: boolean,     // Enable or disable fullscreen icon (mode still available)
    enableGotoPage: boolean,       // A "go to page" jump box
    enableGotoSuggestions: boolean, // Controls whether suggestions are shown under the input field when the user is typing in the 'go to page' form
    enableGridIcon: boolean,       // A grid view of all the pages
    enableGridControls: string,  // Specify control of pages per grid row in Grid view. Possible values: 'buttons' (+/-), 'slider'. Any other value disables the controls.
    enableImageTitles: boolean,    // Adds "Page {n}" title to page images if true
    enableIndexAsLabel: boolean,  // Use index numbers instead of page labels in the page n-m display.
    enableKeyScroll: boolean,      // Captures scrolling using the arrow and page up/down keys regardless of page focus. When off, defers to default browser scrolling behavior.
    enableLinkIcon: boolean,       // Controls the visibility of the link icon
    enableNonPagedVisibilityIcon: boolean, // Controls the visibility of the icon to toggle the visibility of non-paged pages. (Automatically hidden if no 'non-paged' pages).
    enableSpaceScroll: boolean,   // Scrolling down by pressing the space key
    enableToolbar: boolean,        // Enables the toolbar. Note that disabling this means you have to handle all controls yourself.
    enableZoomControls: string, // Specify controls for zooming in and out. Possible values: 'buttons' (+/-), 'slider'. Any other value disables the controls.
    fillParentHeight: boolean,     // Use a flexbox layout to allow Diva to fill its parent's height
    fixedPadding: number,           // Fallback if adaptive padding is set to 0
    fixedHeightGrid: boolean,      // So each page in grid view has the same height (only widths differ)
    goDirectlyTo: number,            // Default initial page to show (0-indexed)
    hashParamSuffix: string | null,      // Used when there are multiple document viewers on a page
    imageCrossOrigin: string, // Set crossOrigin property for image requests
    inFullscreen: boolean,        // Set to true to load fullscreen mode initially
    inBookLayout: boolean,       // Set to true to view the document with facing pages in document mode
    inGrid: boolean,              // Set to true to load grid view initially
    maxPagesPerRow: number,          // Maximum number of pages per row in grid view
    maxZoomLevel: number,           // Optional; defaults to the max zoom returned in the JSON response
    minPagesPerRow: number,          // Minimum pages per row in grid view. Recommended default.
    minZoomLevel: number,            // Defaults to 0 (the minimum zoom)
    onGotoSubmit: (a: string) => number | null,         // When set to a function that takes a string and returns a page index, this will override the default behaviour of the 'go to page' form submission
    pageAliases: object,            // An object mapping specific page indices to aliases (has priority over 'pageAliasFunction'
    pageAliasFunction: (a: number) => string | boolean,  // A function mapping page indices to an alias. If false is returned, default page number is displayed
    pageLoadTimeout: number,       // Number of milliseconds to wait before loading pages
    pagesPerRow: number,             // The default number of pages per row in grid view
    panelWidth: number,
    panelHeight: number,
    plugins: any[],
    requestHeaders: object, // Default header sent off to the server in content negotiation
    showNonPagedPages: boolean,   // Whether pages tagged as 'non-paged' (in IIIF manifests only) should be visible after initial load
    throbberTimeout: number,       // Number of milliseconds to wait before showing throbber
    tileHeight: number,            // The height of each tile, in pixels; usually 256
    tileWidth: number,             // The width of each tile, in pixels; usually 256
    toolbarParentObject: HTMLElement | null,  // The toolbar parent object.
    verticallyOriented: boolean,   // Determines vertical vs. horizontal orientation
    viewportMargin: number,        // Pretend tiles +/- 200px away from viewport are in
    zoomLevel: number
}

export type ViewerSettings = {
    currentPageIndices: Array<number>,    // The visible pages in the viewport
    activePageIndex: number,         // The current 'active' page in the viewport
    horizontalOffset: number,        // Distance from the center of the diva element to the top of the current page
    horizontalPadding: number,       // Either the fixed padding or adaptive padding
    ID: string | null,                   // The prefix of the IDs of the elements (usually 1-diva-)
    initialKeyScroll: boolean,    // Holds the initial state of enableKeyScroll
    initialSpaceScroll: boolean,  // Holds the initial state of enableSpaceScroll
    innerElement: HTMLElement | null,         // The native .diva-outer DOM object
    innerObject: HTMLElement | null,            // document.getElementById(settings.ID + 'inner'), for selecting the .diva-inner element
    isActiveDiva: boolean,         // In the case that multiple diva panes exist on the same page, this should have events funneled to it.
    isScrollable: boolean,         // Used in enable/disableScrollable public methods
    isZooming: boolean,           // Flag to keep track of whether zooming is still in progress, for handleZoom
    loaded: boolean,              // A flag for when everything is loaded and ready to go.
    manifest: ImageManifest | null,
    mobileWebkit: boolean,        // Checks if the user is on a touch device (iPad/iPod/iPhone/Android)
    numPages: number,                // Number of pages in the array
    oldZoomLevel: number,           // Holds the previous zoom level after zooming in or out
    options: Options,
    outerElement: HTMLElement | null,         // The native .diva-outer DOM object
    outerObject: HTMLElement | null,            // document.getElementById(settings.ID + 'outer'), for selecting the .diva-outer element
    pageOverlays: PageOverlayManager,
    pageTools: Array<any>,              // The plugins which are enabled as page tools
    parentObject: HTMLElement, // object referencing the parent element
    pendingManifestRequest: any, // Reference to the xhr request retrieving the manifest. Used to cancel the request on destroy()
    pluginInstances: Array<any>,                // Filled with the enabled plugins from the registry
    renderer: Renderer | null,
    resizeTimer: ReturnType<typeof setTimeout> | null,            // Holds the ID of the timeout used when resizing the window (for clearing)
    scrollbarWidth: number,          // Set to the actual scrollbar width in init()
    selector: string | null,               // Uses the generated ID prefix to easily select elements
    throbberTimeoutID: ReturnType<typeof setTimeout> | null,      // Holds the ID of the throbber loading timeout
    toolbar: object | null,              // Holds an object with some toolbar-related functions
    verticalOffset: number,          // Distance from the center of the diva element to the left side of the current page
    verticalPadding: number,         // Either the fixed padding or adaptive padding
    viewHandler: any,
    viewport: any,             // Object caching the viewport dimensions
    viewportElement: HTMLElement | null,
    viewportObject: HTMLElement | null,
    zoomDuration: number
}

export type MergedConfiguration = ViewerSettings & Options

export interface DivaState
{
    viewerCore: ViewerCore,
    toolbar: any
}

export interface ActiveViewOptions
{
    inGrid?: boolean;
    inBookLayout?: boolean;
    inFullscreen?: boolean;
    zoomLevel?: number;
    pagesPerRow?: number;
    goDirectlyTo?: number;
    horizontalOffset?: number;
    verticalOffset?: number;
    verticallyOriented?: boolean;
    showNonPagedPages?: boolean;
}


export interface HashParameters
{
    f?: string | boolean,
    v?: string,
    z?: string | number,
    n?: string | number,
    i?: string,
    p?: string | number,
    y?: string | number,
    x?: string | number
}

export type ImageRequestOptions = {
    url: string;
    timeoutTime: number;
    settings: any;
    load: any;
    error: any;
}


export type RendererSettings = {
    viewport: any;
    outerElement: HTMLElement;
    innerElement: HTMLElement;
    settings: MergedConfiguration;
}

export interface RendererLoadConfig
{
    pageLayouts: LayoutGroupPages[];
    padding: PaddingDefinitions;
    maxZoomLevel: number | null;
    verticallyOriented: any;
}

export type RendererHooks = {
    onViewWillLoad?: () => void;
    onViewDidLoad?: () => void;
    onViewDidUpdate?: (pages: any, targetPage: any) => void;
    onViewDidTransition?: () => void;
    onPageWillLoad?: (pageIndex: number) => void;
    onZoomLevelWillChange?: (zoomLevel: number) => void;
}

export type RendererViewportPosition = {
    zoomLevel: number;
    anchorPage: number;
    verticalOffset: any;
    horizontalOffset: any;
}

export interface LayoutGroupSettings
{
    manifest: any;
    verticallyOriented?: boolean;
    showNonPagedPages: boolean;
    viewport?: any;
    pagesPerRow?: number;
    fixedHeightGrid?: boolean;
    fixedPadding?: number;
}


export interface ValidationOptions
{
    additionalProperties: any[];
    validations: OptionsValidator[];
    whitelistedKeys?: any[];
}

export interface OptionsValidator
{
    key: string;
    validate: (value: number, settings: MergedConfiguration, config?: any) => (number)
}

export interface PageRegionOptions
{
    includePadding?: boolean;
    incorporateViewport?: boolean;
}
