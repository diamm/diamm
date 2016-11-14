import { combineReducers } from "redux";
import { routerReducer as routing } from "react-router-redux";
import sourceReducer from "./source_reducer";
import userReducer from "./user_reducer";

const rootReducer = combineReducers({
    user: userReducer,
    source: sourceReducer,
    routing
});

export default rootReducer;
