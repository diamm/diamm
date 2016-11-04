import * as React from "react";
import * as ReactDOM from "react-dom";
import { Provider } from "react-redux";
import { Router, useRouterHistory } from 'react-router';
import { createHashHistory } from 'history';
import { syncHistoryWithStore } from 'react-router-redux';

import configureStore from "./store/configure-store";
import routes from './store/routes';

const store = configureStore({});
const appHistory = useRouterHistory(createHashHistory)({ queryKey: false });
const history = syncHistoryWithStore(appHistory, store);

ReactDOM.render(
    <div>
        <Provider store={ store }>
            <Router history={ history }>
                { routes }
            </Router>
        </Provider>
    </div>,
    document.getElementById("source-body")
);
