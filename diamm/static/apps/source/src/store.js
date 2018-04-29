import { createStore, applyMiddleware } from "redux";
import rootReducer from "./reducers";
import thunk from "redux-thunk";

let middlewares = [thunk];

if (process.env.NODE_ENV !== `production`) {
    const { logger } = require(`redux-logger`);
    middlewares.push(logger);
}

export default function configureStore (initialState, history)
{
    middlewares.unshift(history);

    return createStore(
        rootReducer,
        initialState,
        applyMiddleware(...middlewares)
    );
}
