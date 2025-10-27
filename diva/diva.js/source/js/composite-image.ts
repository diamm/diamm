import TileCoverageMap from "./tile-coverage-map";
import {DivaTileAlt, DivaTiledPage, DivaTileSource} from "./viewer-type-definitions";
import ImageCache from "./image-cache";

/**
 * @class CompositeImage
 * @private
 *
 * Utility class to composite tiles into a complete image
 * and track the rendered state of an image as new tiles
 * load.
 */

export default class CompositeImage
{
    _levels: DivaTiledPage[];
    _urlsToTiles: Record<string, DivaTileAlt>;
    _loadedByLevel: Record<number, TileCoverageMap>;

    constructor(levels: DivaTiledPage[])
    {
        this._levels = levels;  // Assume levels sorted high-res first
        const urlsToTiles: Record<string, DivaTileAlt> = this._urlsToTiles = {};

        levels.forEach(level =>
        {
            level.tiles.forEach((tile: DivaTileSource) =>
            {
                urlsToTiles[tile.url] = {
                    zoomLevel: level.zoomLevel,
                    row: tile.row,
                    col: tile.col
                };
            });
        });

        this.clear();
    }

    clear ()
    {
        const loadedByLevel: Record<number, TileCoverageMap> = this._loadedByLevel = {};

        this._levels.forEach((level) => {
            loadedByLevel[level.zoomLevel] = new TileCoverageMap(level.rows, level.cols);
        });
    }

    getTiles (baseZoomLevel: number | null): DivaTileSource[]
    {
        const toRenderByLevel: DivaTileSource[][] = [];
        const highestZoomLevel = this._levels[0].zoomLevel;
        const covered = new TileCoverageMap(this._levels[0].rows, this._levels[0].cols);

        let bestLevelIndex;

        // Default to the lowest zoom level
        if (baseZoomLevel === null)
        {
            bestLevelIndex = 0;
        }
        else
        {
            const ceilLevel = Math.ceil(baseZoomLevel);
            bestLevelIndex = findIndex(this._levels, (level: DivaTiledPage): boolean => level.zoomLevel <= ceilLevel);
            // bestLevelIndex = this._levels.findIndex((level) => level.zoomLevel <= ceilLevel);
        }


        // The best level, followed by higher-res levels in ascending order of resolution,
        // followed by lower-res levels in descending order of resolution
        const levelsByPreference = this._levels.slice(0, bestLevelIndex + 1).reverse()
            .concat(this._levels.slice(bestLevelIndex + 1));

        levelsByPreference.forEach( (level: DivaTiledPage) =>
        {
            const loaded: TileCoverageMap = this._loadedByLevel[level.zoomLevel];

            let additionalTiles: DivaTileSource[] = level.tiles.filter(tile => loaded.isLoaded(tile.row, tile.col));

            // Filter out entirely covered tiles

            // FIXME: Is it better to draw all of a partially covered tile,
            // with some of it ultimately covered, or to pick out the region
            // which needs to be drawn?
            // See https://github.com/DDMAL/diva.js/issues/358
            const scaleRatio = Math.pow(2, highestZoomLevel - level.zoomLevel);

            additionalTiles = additionalTiles.filter(tile => {
                let isNeeded = false;

                const highResRow = tile.row * scaleRatio;
                const highResCol = tile.col * scaleRatio;

                for (let i=0; i < scaleRatio; i++)
                {
                    for (let j=0; j < scaleRatio; j++)
                    {
                        if (!covered.isLoaded(highResRow + i, highResCol + j))
                        {
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

        const tiles: DivaTileSource[] = [];

        toRenderByLevel.forEach((byLevel: DivaTileSource[]) => {
            tiles.push.apply(tiles, byLevel);
        });

        return tiles;
    }

    /**
     * Update the composite image to take into account all the URLs
     * loaded in an image cache.
     *
     * @param cache {ImageCache}
     */
    updateFromCache (cache: ImageCache)
    {
        this.clear();

        this._levels.forEach( (level: DivaTiledPage) =>
        {
            const loaded: TileCoverageMap = this._loadedByLevel[level.zoomLevel];

            level.tiles.forEach(tile => {
                if (cache.has(tile.url))
                {
                    loaded.set(tile.row, tile.col, true);
                }
            });
        }, this);
    }

    updateWithLoadedUrls (urls: string[])
    {
        urls.forEach( (url: string) =>
        {
            const entry = this._urlsToTiles[url];
            this._loadedByLevel[entry.zoomLevel].set(entry.row, entry.col, true);
        });
    }
}

// function fill (count, value)
// {
//     const arr = new Array(count);
//
//     for (let i=0; i < count; i++)
//         arr[i] = value;
//
//     return arr;
// }

function findIndex (array: any[], predicate: ((a: any, b: any) => boolean)): number
{
    const length = array.length;
    for (let i = 0; i < length; i++)
    {
        if (predicate(array[i], i))
        {
            return i;
        }
    }

    return -1;
}
