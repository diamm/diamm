import {
    IIIF_MANIFEST_DID_LOAD,
    IIIF_SET_CURRENTLY_ACTIVE_RANGES,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS_TITLE,
    IIIF_SET_COMPUTED_RANGE_LOOKUP
} from "../constants";
import _ from "lodash";


export function computeRangeLookup (structures)
{
    let ranges = {};

    structures.map( (entry) =>
    {
        let range = entry["@id"];
        entry.members.map( (member) =>
        {
            let canvas = member["@id"];
            _.has(ranges, canvas) ? _.concat(ranges[canvas], [range]) : ranges[canvas] = [range];
        })
    });
    return {
        type: IIIF_SET_COMPUTED_RANGE_LOOKUP,
        ranges
    }
}

export function setActiveManifest (manifest)
{
    return (dispatch) =>
    {
        dispatch(computeRangeLookup(manifest.structures))

        return dispatch({
            type: IIIF_MANIFEST_DID_LOAD,
            manifest
        });
    };
}

export function loadPageData (manifest)
{

}

export function setCurrentlyActiveRanges (ranges)
{
    return {
        type: IIIF_SET_CURRENTLY_ACTIVE_RANGES,
        ranges
    }
}

export function fetchActiveRanges (ranges)
{
    return (dispatch) =>
    {
        dispatch(setCurrentlyActiveRanges(ranges));

        dispatch( () => ranges.map( (range) => {
            console.log('fetching', range);
        }));
    };

    // return {
    //     type: IIIF_SET_CURRENTLY_ACTIVE_RANGES,
    //     ranges
    // }
}

export function setCurrentlyActiveCanvas (canvas)
{
    return {
        type: IIIF_SET_CURRENTLY_ACTIVE_CANVAS,
        canvas
    }
}

export function setCurrentlyActiveCanvasTitle (title)
{
    return {
        type: IIIF_SET_CURRENTLY_ACTIVE_CANVAS_TITLE,
        title
    }
}
