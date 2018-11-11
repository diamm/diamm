import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Router } from "react-router";
import createBrowserHistory from 'history/createBrowserHistory';
import { routerMiddleware } from "react-router-redux";

import configureStore from "./store";
import routes from "./routes";

const history = createBrowserHistory();
const historyMiddleware = routerMiddleware(history);

export const store = configureStore({}, historyMiddleware);


ReactDOM.render(
    <Provider store={ store }>
        <Router history={ history }>
            { routes }
        </Router>
    </Provider>,
    document.getElementById("search-body")
);
