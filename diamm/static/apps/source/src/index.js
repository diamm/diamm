import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { ConnectedRouter } from 'connected-react-router'

import configureStore, { history } from "./store";

import routes from "./routes";
export const store = configureStore({});

ReactDOM.render(
    <Provider store={ store } >
        <ConnectedRouter history={ history }>
            { routes }
        </ConnectedRouter>
    </Provider>,
    document.getElementById("source-body")
);
