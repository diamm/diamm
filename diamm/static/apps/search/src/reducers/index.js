import { combineReducers } from "redux";
import { routerReducer as routing } from "react-router-redux";
import currentQueryReducer from "./current_query";
import resultsReducer from "./results";
import facetsReducer from "./facets";


const rootReducer = combineReducers({
    currentQuery: currentQueryReducer,
    results: resultsReducer,
    facets: facetsReducer,
    routing
});

export default rootReducer;
