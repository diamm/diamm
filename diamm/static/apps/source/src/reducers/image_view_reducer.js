import {
    IIIF_SET_CURRENTLY_ACTIVE_RANGES,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS_TITLE,
    IIIF_SET_COMPUTED_RANGE_LOOKUP
} from "../constants";
const INITIAL_STATE = {
    activeRanges: null,
    activeCanvas: null,
    activeCanvasTitle: null,
    ranges: null
};

export default function imageViewReducer (state=INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (IIIF_SET_CURRENTLY_ACTIVE_RANGES):
            return { ...state, "activeRanges": action.ranges };
        case (IIIF_SET_CURRENTLY_ACTIVE_CANVAS):
            return { ...state, "activeCanvas": action.canvas };
        case (IIIF_SET_CURRENTLY_ACTIVE_CANVAS_TITLE):
            return { ...state, "activeCanvasTitle": action.title };
        case (IIIF_SET_COMPUTED_RANGE_LOOKUP):
            return { ...state, "ranges": action.ranges };
        default:
            return state;
    }
}
