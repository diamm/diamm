import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { HashRouter } from "react-router-dom";
import createBrowserHistory from "history/createBrowserHistory";
import { routerMiddleware } from "react-router-redux";

import configureStore from "./store";
import routes from "./routes";
import { setActiveTab } from "./actions/index";

const history = createBrowserHistory();
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
history.listen( (location, action) => {
    // we're only interested in the 'PUSH' actions
    console.log(location);
    console.log(action);

    if (action === POP)
        return null;

    store.dispatch(setActiveTab(location));
});


ReactDOM.render(
    <Provider store={ store } >
        <HashRouter history={ history } >
            { routes }
        </HashRouter>
    </Provider>,
    document.getElementById("source-body")
);
