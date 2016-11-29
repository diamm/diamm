import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Router, browserHistory } from "react-router";
import { syncHistoryWithStore } from "react-router-redux";

import configureStore from "./store";
import routes from "./routes";

export const store = configureStore({});
const history = syncHistoryWithStore(browserHistory, store);


ReactDOM.render(
    <Provider store={ store }>
        <Router history={ history }>
            { routes }
        </Router>
    </Provider>,
    document.getElementById("search-body")
);
