import { combineReducers } from "redux-immutable";
// import { routerReducer as routing } from "react-router-redux";
import Immutable from "immutable";
import { LOCATION_CHANGE } from "react-router-redux";


const initialState = Immutable.fromJS({
    locationBeforeTransitions: null
});

function routing (state = initialState, action)
{
    if (action.type === LOCATION_CHANGE) {
        return state.set('locationBeforeTransitions', action.payload);
    }

    return state;
}

const rootReducer = combineReducers({
    routing
});

export default rootReducer;
