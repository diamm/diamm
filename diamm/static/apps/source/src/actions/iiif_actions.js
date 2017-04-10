import {
    IIIF_MANIFEST_DID_LOAD,
    IIIF_SET_CURRENTLY_ACTIVE_RANGES,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS_TITLE,
    IIIF_SET_COMPUTED_RANGE_LOOKUP,
    IIIF_CLEAR_PAGE_CONTENTS,
    IIIF_ADD_TO_PAGE_CONTENTS,
    IIIF_IS_FETCHING_PAGE_CONTENTS,
    IIIF_FINISHED_FETCHING_PAGE_CONTENTS
} from "../constants";
import _ from "lodash";


export function computeRangeLookup (structures)
{
    let ranges = {};

    structures.map( (entry) =>
    {
        let range = entry;
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
        dispatch(computeRangeLookup(manifest.structures));

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
    return (dispatch, getState) =>
    {
        let state = getState();
        let isFetching = state.image_view.isFetchingPageContents;

        // bail early if we're already fetching
        if (isFetching)
            return;

        dispatch(setCurrentlyActiveRanges(ranges));

        ranges.map( (range) => {
            fetch(range.service['@id'])
                .then((response) =>
                {
                    dispatch({
                        type: IIIF_FINISHED_FETCHING_PAGE_CONTENTS
                    });
                    return response.json()
                }).then((data) =>
                {
                    dispatch({
                        type: IIIF_CLEAR_PAGE_CONTENTS
                    });

                    dispatch({
                        type: IIIF_ADD_TO_PAGE_CONTENTS,
                        item: data
                    });
                });
        });
    };
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

export function clearPageContents ()
{
    return {
        type: IIIF_CLEAR_PAGE_CONTENTS
    }
}
