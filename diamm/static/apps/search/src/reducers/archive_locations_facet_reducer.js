import {
    UPDATE_ARCHIVE_LOCATION_FACET,
    RESET_ARCHIVE_LOCATION_FACET
} from "../constants";

const INITIAL_STATE = {
    activeType: null,
    activeSelect: null,
    activeParent: null
};

export default function archiveLocations (state = INITIAL_STATE, action)
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
            return INITIAL_STATE;
        default:
            return state;
    }
}
