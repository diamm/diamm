import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Route } from "react-router";
import { BrowserRouter as Router } from "react-router-dom";

import configureStore from "./store";
import App from "./components/app";

export const store = configureStore({});
export const ROOT_ROUTE = "/search/";

ReactDOM.render(
    <Provider store={ store }>
        <Router>
            <Route path={ ROOT_ROUTE } component={ App } />
        </Router>
    </Provider>,
    document.getElementById("search-body")
);
