import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Router, browserHistory } from "react-router";
import { Map, fromJS } from "immutable";
import { syncHistoryWithStore } from "react-router-redux";
import { createSelectLocationState } from "./utils/route-state-helper";

import configureStore from "./store";
import routes from "./routes";

const INITIAL_STATE = Map();

export const store = configureStore(INITIAL_STATE);
const history = syncHistoryWithStore(
    browserHistory,
    store,
    {
        selectLocationState (state) {
            return state.get('routing').toObject();
        }
    }
);

ReactDOM.render(
    <Provider store={ store }>
        <Router history={ history }>
            { routes }
        </Router>
    </Provider>,
    document.getElementById('catalogue-body')
);
