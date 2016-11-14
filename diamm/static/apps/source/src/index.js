import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Router, useRouterHistory } from "react-router";
import { createHashHistory } from "history";
import { syncHistoryWithStore } from "react-router-redux";

import configureStore from "./store";
import routes from "./routes";

const store = configureStore({});
const appHistory = useRouterHistory(createHashHistory)();
const history = syncHistoryWithStore(appHistory, store);


ReactDOM.render(
    <Provider store={ store } >
        <Router history={ history } >
            { routes }
        </Router>
    </Provider>,
    document.getElementById("source-body")
);
