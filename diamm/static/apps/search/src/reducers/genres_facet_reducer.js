import {
    ADD_GENRE_TO_ACTIVE,
    CLEAR_ACTIVE_GENRES,
    REMOVE_GENRE_FROM_ACTIVE,
    RESET_GENRES_FACET
} from "../constants";


const INITIAL_STATE = {
    show_all: false,
    active: [],
    facetValue: null
};

export default function genres (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (RESET_GENRES_FACET):
            return INITIAL_STATE;
        case (ADD_GENRE_TO_ACTIVE):
            // if it's already in the array, don't add it again!
            if (state.active.indexOf(action.value) === -1)
                return { ...state, active: state.active.concat([action.value])};
            else
                return { ...state, active: state.active };
        case (CLEAR_ACTIVE_GENRES):
            return { ...state, active: []};
        case (REMOVE_GENRE_FROM_ACTIVE):
            return { ...state, active: state.active.filter(c => c !== action.value)};
        default:
            return state;
    }
}
