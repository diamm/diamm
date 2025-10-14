import parseIIIFManifest from './parse-iiif-manifest';
import IIIFSourceAdapter from "./iiif-source-adapter";
import {
    Dimension,
    DivaServiceBlock,
    DivaTiledPage,
    DivaTileSource,
    HWDimension,
    OptionalDimension
} from "./viewer-type-definitions";


export default class ImageManifest
{
    pages: any[];
    maxZoom: number;
    maxRatio: number;
    minRatio: number;
    itemTitle: string;
    metadata: object;
    paged: boolean;
    _maxWidths: number[];
    _maxHeights: number[];
    _averageWidths: number[];
    _averageHeights: number[];
    _totalHeights: number[];
    _totalWidths: number[];
    _urlAdapter: IIIFSourceAdapter;

    constructor (data: DivaServiceBlock, urlAdapter: IIIFSourceAdapter)
    {
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

    static fromIIIF (iiifManifest: object): ImageManifest
    {
        const data: DivaServiceBlock = parseIIIFManifest(iiifManifest)!;
        return new ImageManifest(data, new IIIFSourceAdapter());
    }

    isPageValid (pageIndex: number, showNonPagedPages: boolean): boolean
    {
        if (!showNonPagedPages && this.paged && !this.pages[pageIndex].paged)
        {
            return false;
        }

        return pageIndex >= 0 && pageIndex < this.pages.length;
    }

    getMaxPageDimensions (pageIndex: number): Dimension
    {
        const maxDims: HWDimension = this.pages[pageIndex].d[this.maxZoom];

        return {
            height: maxDims.h,
            width: maxDims.w
        };
    }

    getPageDimensionsAtZoomLevel (pageIndex: number, zoomLevel: number): Dimension
    {
        const maxDims: HWDimension = this.pages[pageIndex].d[this.maxZoom];

        const scaleRatio: number = getScaleRatio(this.maxZoom, zoomLevel);

        return {
            height: maxDims.h * scaleRatio,
            width: maxDims.w * scaleRatio
        };
    }

    /**
     * Returns a URL for the image of the given page. The optional size
     * parameter supports setting the image width or height (default is
     * full-sized).
     */
    getPageImageURL (pageIndex: number, size: OptionalDimension): string
    {
        return this._urlAdapter.getPageImageURL(this, pageIndex, size);
    }

    /**
     * Return an array of tile objects for the specified page and integer zoom level
     */
    getPageImageTiles (pageIndex: number, zoomLevel: number, tileDimensions: Dimension): DivaTiledPage
    {
        const page = this.pages[pageIndex];

        if (!isFinite(zoomLevel) || zoomLevel % 1 !== 0)
        {
            throw new TypeError('Zoom level must be an integer: ' + zoomLevel);
        }

        const rows = Math.ceil(page.d[zoomLevel].h / tileDimensions.height);
        const cols = Math.ceil(page.d[zoomLevel].w / tileDimensions.width);

        const tiles: DivaTileSource[] = [];

        let row, col, url;

        for (row = 0; row < rows; row++)
        {
            for (col = 0; col < cols; col++)
            {
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

    getAverageWidth (zoomLevel: number): number
    {
        return this._averageWidths[zoomLevel]
    }

    getAverageHeight (zoomLevel: number): number
    {
        return this._averageHeights[zoomLevel]
    }

    getMaxWidth (zoomLevel: number): number
    {
        return this._maxWidths[zoomLevel]
    }

    getMaxHeight (zoomLevel: number): number
    {
        return this._maxHeights[zoomLevel]
    }

    getTotalWidth (zoomLevel: number): number
    {
        return this._totalWidths[zoomLevel]
    }

    getTotalHeight (zoomLevel: number): number
    {
        return this._totalHeights[zoomLevel]
    }
}

function getScaleRatio (sourceZoomLevel: number, targetZoomLevel: number): number
{
    return 1 / Math.pow(2, sourceZoomLevel - targetZoomLevel);
}
