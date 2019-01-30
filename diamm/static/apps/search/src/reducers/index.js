import { combineReducers } from "redux";
import currentQuery from "./current_query";
import currentQueryType from "./current_query_type";
import currentFacets from "./current_facets";
import results from "./results";


const rootReducer = combineReducers({
    currentQuery,
    currentFacets,
    currentQueryType,
    results
});

export default rootReducer;
