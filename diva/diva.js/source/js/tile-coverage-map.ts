export default class TileCoverageMap
{
    _rows: number;
    _cols: number;
    _map: boolean[][];

    constructor (rows: number, cols: number)
    {
        this._rows = rows;
        this._cols = cols;
        this._map = new Array(rows).fill(null).map(() => new Array(cols).fill(false));
    }

    isLoaded (row: number, col: number): boolean
    {
        // Return true for out of bounds tiles because they
        // don't need to load. (Unfortunately this will also
        // mask logical errors.)
        if (row >= this._rows || col >= this._cols)
        {
            return true;
        }

        return this._map[row][col];
    }

    set(row: number, col: number, value: boolean)
    {
        this._map[row][col] = value;
    }
}
