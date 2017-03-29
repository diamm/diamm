import {
    IIIF_SET_CURRENTLY_ACTIVE_RANGES,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS,
    IIIF_SET_CURRENTLY_ACTIVE_CANVAS_TITLE,
    IIIF_SET_COMPUTED_RANGE_LOOKUP,
    IIIF_CLEAR_PAGE_CONTENTS,
    IIIF_ADD_TO_PAGE_CONTENTS,
    IIIF_IS_FETCHING_PAGE_CONTENTS,
    IIIF_FINISHED_FETCHING_PAGE_CONTENTS
} from "../constants";
const INITIAL_STATE = {
    activeRanges: null,
    activeCanvas: null,
    activeCanvasLabel: null,
    ranges: null,
    isFetchingPageContents: false,
    pageContents: []
};

export default function imageViewReducer (state=INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (IIIF_SET_CURRENTLY_ACTIVE_RANGES):
            return { ...state, activeRanges: action.ranges };
        case (IIIF_SET_CURRENTLY_ACTIVE_CANVAS):
            return { ...state, activeCanvas: action.canvas };
        case (IIIF_SET_CURRENTLY_ACTIVE_CANVAS_TITLE):
            return { ...state, activeCanvasLabel: action.title };
        case (IIIF_SET_COMPUTED_RANGE_LOOKUP):
            return { ...state, ranges: action.ranges };
        case (IIIF_CLEAR_PAGE_CONTENTS):
            return { ...state, pageContents: []};
        case (IIIF_ADD_TO_PAGE_CONTENTS):
            return { ...state, pageContents: [...state.pageContents, action.item]};
        case (IIIF_IS_FETCHING_PAGE_CONTENTS):
            return { ...state, isFetchingPageContents: true};
        case (IIIF_FINISHED_FETCHING_PAGE_CONTENTS):
            return { ...state, isFetchingPageContents: false};
        default:
            return state;
    }
}
