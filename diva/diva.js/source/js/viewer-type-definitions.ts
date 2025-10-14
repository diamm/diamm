export type Region = {
    top: number,
    bottom: number,
    left: number,
    right: number
}

export type XYPos = {
    x: number;
    y: number;
}

export type PageXYPos = {
    pageX: number;
    pageY: number;
}

export type Dimension = {
    width: number;
    height: number;
}

export interface OptionalDimension
{
    width?: number;
    height?: number;
}

export type HWDimension = {
    h: number;
    w: number;
}

export type Offset = {
    top: number;
    left: number;
}

export interface PaddingDefinitions
{
    document: Region;
    page: Region;
}

export interface PageGroup
{
    index: number;
    dimensions: Dimension;
    pages: LayoutGroupPage[];
    region: any;
    padding: any;
}


export type PageInfo = {
    index: number;
    group: PageGroup;
    dimensions: Dimension;
    groupOffset: Offset;
}

export type PageInfoCollection = { [n: number] : PageInfo }


export interface DivaPage
{
    d: HWDimension[];
    m: number;
    l: string;
    il: string | null;
    f: string;
    url: string;
    api: number;
    paged: boolean;
    facingPages: boolean;
    canvas: any;
    otherImages: any[];
    xoffset: number | null;
    yoffset: number | null;
}

export interface DivaSecondaryPage
{
    f: string;
    url: string;
    il: string;
    d: HWDimension[]
}

export interface DivaImageInfo
{
    url: string;
    x?: number;
    y?: number;
    w?: number;
    h?: number;
}

export interface DivaServiceBlock
{
    version: number;
    item_title: string;
    metadata: any;
    dims: DivaDimensionMeasurements;
    max_zoom: number;
    pgs: DivaPage[];
    paged: boolean;
}

export interface DivaDimensionMeasurements
{
    a_wid: number[];
    a_hei: number[];
    max_w: number[];
    max_h: number[];
    max_ratio: number;
    min_ratio: number;
    t_hei: number[];
    t_wid: number[];
}


export type DivaTileSource = {
    zoomLevel: number;
    row: number;
    col: number;
    dimensions: Dimension;
    offset: Offset;
    url: string;
}

export interface DivaTileAlt
{
    zoomLevel: number;
    row: number;
    col: number;
}

export type ScaledDivaTileSource = {
    sourceZoomLevel: number,
    scaleRatio: number,
    row: number,
    col: number,
    dimensions: Dimension,
    offset: Offset,
    url: string
}

export interface DivaTiledPage
{
    zoomLevel: number;
    rows: number;
    cols: number;
    tiles: DivaTileSource[];
}

export interface SourceProvider
{
    getAllZoomLevelsForPage: (page: PageInfo) => DivaTiledPage[]
    getBestZoomLevelForPage: (page: PageInfo) => DivaTiledPage
}

export interface DivaTiledRequestParams
{
    row: number;
    col: number;
    rowCount: number;
    colCount: number;
    zoomLevel: number;
    tileDimensions: Dimension
}

export interface LayoutGroupPages
{
    dimensions: Dimension;
    pages: LayoutGroupPage[];
}

export interface LayoutGroupPage
{
    index: number;
    groupOffset: Offset;
    dimensions: Dimension
}


export interface BookLayoutPage
{
    index: number;
    dimensions: Dimension;
    paged: boolean;
}

export interface PagePosition
{
    anchorPage: number;
    offset: Offset;
}

export interface ViewportSize
{
    top: number;
    left: number;
    bottom: number;
    right: number;
    width: number;
    height: number;
}
