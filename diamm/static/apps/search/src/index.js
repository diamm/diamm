import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Router } from "react-router";
import createBrowserHistory from 'history/createBrowserHistory';
import { syncHistoryWithStore } from "react-router-redux";

import configureStore from "./store";
import routes from "./routes";

const histobj = createBrowserHistory();

export const store = configureStore({});
const history = syncHistoryWithStore(histobj, store);


ReactDOM.render(
    <Provider store={ store }>
        <Router history={ history }>
            { routes }
        </Router>
    </Provider>,
    document.getElementById("search-body")
);
