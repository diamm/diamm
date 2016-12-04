import {
    FACET_UPDATE_COMPOSER_TOGGLE,
    FACET_UPDATE_GENRE_TOGGLE,
    UPDATE_ARCHIVE_LOCATION_FACET,
    RESET_ARCHIVE_LOCATION_FACET,
    UPDATE_CURRENT_COMPOSER_VALUE,
    RESET_COMPOSERS_FACET
} from "../constants";
import { combineReducers } from "redux";

const INITIAL_FACET_STATE = {
    show_all: false,
    active: [],
    facetValue: null
};

const INITIAL_COMPOSER_FACET_STATE = {
    active: [],
    facetValue: ""
};

function composers (state = INITIAL_COMPOSER_FACET_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_CURRENT_COMPOSER_VALUE):
            return { ...state, facetValue: action.value };
        case (RESET_COMPOSERS_FACET):
            return INITIAL_COMPOSER_FACET_STATE;
        default:
            return state;
    }
}

function genres (state = INITIAL_FACET_STATE, action)
{
    switch (action.type)
    {
        case (FACET_UPDATE_GENRE_TOGGLE):
            return { ...state, show_all: action.toggle };
        default:
            return state;
    }
}

const INITIAL_ARCHIVE_LOCATION_STATE = {
    activeType: null,
    activeSelect: null,
    activeParent: null
};

function archiveLocations (state = INITIAL_ARCHIVE_LOCATION_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_ARCHIVE_LOCATION_FACET):
            return {
                activeType: action.activeType,
                activeSelect: action.activeSelect,
                activeParent: action.activeParent
            };
        case (RESET_ARCHIVE_LOCATION_FACET):
            return {
                activeType: null,
                activeSelect: null,
                activeParent
            };
        default:
            return state;
    }
}

const currentFacets = combineReducers({
    composers,
    genres,
    archiveLocations
});

export default currentFacets;
