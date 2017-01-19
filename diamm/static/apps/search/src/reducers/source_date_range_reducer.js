import {
    SOURCE_DATE_CLEAR_END_VALUE,
    SOURCE_DATE_CLEAR_START_VALUE,
    SOURCE_DATE_END_VALUE,
    SOURCE_DATE_START_VALUE,
    RESET_SOURCE_DATE_RANGE_FACET
} from "../constants";


const INITIAL_STATE = {
    dateRangeStart: null,
    dateRangeEnd: null
};

export default function dateRange (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_SOURCE_DATE_RANGE_FACET):
            return INITIAL_STATE;
        case (SOURCE_DATE_START_VALUE):
            return { ...state, dateRangeStart: action.value };
        case (SOURCE_DATE_END_VALUE):
            return { ...state, dateRangeEnd: action.value };
        case (SOURCE_DATE_CLEAR_START_VALUE):
            return { ...state, dateRangeStart: null };
        case (SOURCE_DATE_CLEAR_END_VALUE):
            return { ...state, dateRangeEnd: null };
        default:
            return state;
    }
}
