import { compose, createStore, applyMiddleware } from "redux";
import { routerMiddleware } from 'connected-react-router'
import createRootReducer from "./reducers";
import thunk from "redux-thunk";
import createHashHistory from "history/createHashHistory";

export const history = createHashHistory();

let middlewares = [thunk, routerMiddleware(history)];

if (process.env.NODE_ENV !== `production`) {
    const { logger } = require(`redux-logger`);
    middlewares.push(logger);
}

export default function configureStore (initialState)
{
    const store = createStore(
        createRootReducer(history),
        initialState,
        compose(
            applyMiddleware(...middlewares)
        ),
    );

    return store;
}
