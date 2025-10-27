import {Region} from "./viewer-type-definitions";


export default class Viewport
{
    intersectionTolerance: number;
    outer: HTMLElement;
    _top: number | null;
    _left: number | null;
    _width: number | null;
    _height: number | null;
    _innerDimensions: any;
    top: number;
    bottom: number;
    left: number;
    right: number;

    constructor (outer: HTMLElement, options: { intersectionTolerance?: any; })
    {
        options = options || {};

        this.intersectionTolerance = options.intersectionTolerance || 0;
        this.outer = outer;
        this._top = this._left = this._width = this._height = this._innerDimensions = null;

        this.invalidate();
    }

    intersectsRegion (region: Region): boolean
    {
        return this.hasHorizontalOverlap(region) && this.hasVerticalOverlap(region);
    }

    hasVerticalOverlap (region: Region): boolean
    {
        const top = this.top - this.intersectionTolerance;
        const bottom = this.bottom + this.intersectionTolerance;

        return (
            fallsBetween(region.top, top, bottom) ||
            fallsBetween(region.bottom, top, bottom) ||
            (region.top <= top && region.bottom >= bottom)
        );
    }

    hasHorizontalOverlap (region: Region): boolean
    {
        const left = this.left - this.intersectionTolerance;
        const right = this.right + this.intersectionTolerance;

        return (
            fallsBetween(region.left, left, right) ||
            fallsBetween(region.right, left, right) ||
            (region.left <= left && region.right >= right)
        );
    }

    invalidate ()
    {
        // FIXME: Should this check the inner dimensions as well?
        this._width = this.outer.clientWidth;
        this._height = this.outer.clientHeight;

        this._top = this.outer.scrollTop;
        this._left = this.outer.scrollLeft;
    }

    setInnerDimensions (dimensions: { height: number; width: number; })
    {
        this._innerDimensions = dimensions;

        if (dimensions)
        {
            this._top = clamp(this._top, 0, dimensions.height - this._height);
            this._left = clamp(this._left, 0, dimensions.width - this._width);
        }
    }
}

Object.defineProperties(Viewport.prototype, {
    top: getCoordinateDescriptor('top', 'height'),
    left: getCoordinateDescriptor('left', 'width'),

    width: getDimensionDescriptor('width'),
    height: getDimensionDescriptor('height'),

    bottom: {
        get: function ()
        {
            return this._top + this._height;
        }
    },
    right: {
        get: function ()
        {
            return this._left + this._width;
        }
    }
});

function getCoordinateDescriptor (coord: string, associatedDimension: string)
{
    const privateProp = '_' + coord;
    const source = 'scroll' + coord.charAt(0).toUpperCase() + coord.slice(1);

    return {
        get: function ()
        {
            return this[privateProp];
        },
        set: function (newValue: number)
        {
            let normalized;

            if (this._innerDimensions)
            {
                const maxAllowed = this._innerDimensions[associatedDimension] - this[associatedDimension];
                normalized = clamp(newValue, 0, maxAllowed);
            }
            else
            {
                normalized = clampMin(newValue, 0);
            }

            this[privateProp] = this.outer[source] = normalized;
        }
    };
}

function getDimensionDescriptor (dimen: string)
{
    return {
        get: function ()
        {
            return this['_' + dimen];
        }
    };
}

function fallsBetween (point: number, start: number, end: number): boolean
{
    return point >= start && point <= end;
}

function clamp (value: number, min: number, max: number): number
{
    return clampMin(clampMax(value, max), min);
}

function clampMin (value: number, min: number): number
{
    return Math.max(value, min);
}

function clampMax (value: number, max: number): number
{
    return Math.min(value, max);
}
