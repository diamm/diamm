import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
// import { Router } from "react-router";
import createHistory from "history/createBrowserHistory";
import { ConnectedRouter, routerMiddleware } from "react-router-redux";

import configureStore from "./store";
import routes from "./routes";
import { setActiveTab } from "./actions/index";

const history = createHistory();
const historyMiddleware = routerMiddleware(history);

export const store = configureStore({}, historyMiddleware);
// const appHistory = useRouterHistory(createHashHistory)();

const PUSH = "PUSH";
const POP = "POP";

/*
*
* This enables the active tab switching by listening for the route switching
* action and dispatching the action to set the active tab state.
*
* */
history.listen( (location) => {
    // we're only interested in the 'PUSH' actions
    if (location.action === POP)
        return null;

    store.dispatch(setActiveTab(location))
});


ReactDOM.render(
    <Provider store={ store } >
        <ConnectedRouter history={ history } >
            { routes }
        </ConnectedRouter>
    </Provider>,
    document.getElementById("source-body")
);
