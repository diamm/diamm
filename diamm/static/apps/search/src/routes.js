import React from "react";
import { Route } from "react-router";
import App from "./components/app";

export const ROOT_ROUTE = "/search/";

export default (
    <Route path={ ROOT_ROUTE } component={ App } />
);
