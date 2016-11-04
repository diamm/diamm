import { combineReducers } from "redux";
import { routerReducer as routing } from "react-router-redux";

function tabs(state = 0, action: any)
{
    return state;
}


// manage the state tree. State tree keys and reducer functions should be named the same thing.
const rootReducer = combineReducers({
    tabs,
    routing
});

export default rootReducer;
