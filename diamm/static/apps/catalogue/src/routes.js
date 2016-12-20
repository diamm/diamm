import React from "react";
import { Route } from "react-router";
import App from "./components/app";

import Source from "./components/source";
import Archive from "./components/archive";
import Person from "./components/person";

import {
    ROOT_ROUTE,
    SOURCE_ROUTE,
    ARCHIVE_ROUTE,
    PERSON_ROUTE
} from "./constants";

export default (
    <Route path={ ROOT_ROUTE } component={ App }>
        <Route path={ SOURCE_ROUTE } component={ Source } />
        <Route path={ PERSON_ROUTE } component={ Person } />
        <Route path={ ARCHIVE_ROUTE } component={ Archive } />
    </Route>
);
