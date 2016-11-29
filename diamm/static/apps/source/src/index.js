import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Router, useRouterHistory } from "react-router";
import { createHashHistory } from "history";
import { syncHistoryWithStore } from "react-router-redux";

import configureStore from "./store";
import routes from "./routes";
import { setActiveTab } from "./actions/index";

export const store = configureStore({});
const appHistory = useRouterHistory(createHashHistory)();
const history = syncHistoryWithStore(appHistory, store);

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
        <Router history={ history } >
            { routes }
        </Router>
    </Provider>,
    document.getElementById("source-body")
);
