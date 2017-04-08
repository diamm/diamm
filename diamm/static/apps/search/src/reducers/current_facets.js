import { combineReducers } from "redux";
import notations from "./notations_facet_reducer";
import sourceTypes from "./source_type_facet_reducer";
import hasInventory from "./has_inventory_reducer";
import genres from "./genres_facet_reducer";
import composers from "./composers_facet_reducer";
import archiveLocations from "./archive_locations_facet_reducer";
import anonymous from "./anonymous_reducer";
import dateRange from "./source_date_range_reducer";
import organizationTypes from "./organization_type_facet_reducer";


const currentFacets = combineReducers({
    composers,
    genres,
    archiveLocations,
    notations,
    sourceTypes,
    hasInventory,
    anonymous,
    dateRange,
    organizationTypes
});

export default currentFacets;
