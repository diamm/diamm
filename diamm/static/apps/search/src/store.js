import { createStore, applyMiddleware } from "redux";
import thunk from "redux-thunk";

import rootReducer from "./reducers";

let middlewares = [thunk];

if (process.env.NODE_ENV !== `production`) {
    const createLogger = require(`redux-logger`);
    const logger = createLogger();
    middlewares.push(logger);
}


export default function configureStore (initialState)
{
    return createStore(
        rootReducer,
        initialState,
        applyMiddleware(...middlewares)
    );
}
