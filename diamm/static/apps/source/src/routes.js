import React from "react";
import {Route, Switch, matchPath} from "react-router";
import App from "./components/app";
import Description from "./components/description";
import InventoryByOrder from "./components/inventory_by_order";
import InventoryByComposer from "./components/inventory_by_composer";
import InventoryAlphabetical from "./components/inventory_alphabetical";
import Images from "./components/images";
import Sets from "./components/sets";
import Bibliography from "./components/bibliography";
import CommentaryPublic from "./components/commentary_public";
import CommentaryPrivate from "./components/commentary_private";
import Contributors from "./components/contributors";
import Corrections from "./components/corrections"

export const ROOT_ROUTE = "/";
export const INVENTORY_ROUTE = "/inventory";
export const IMAGES_ROUTE = "/images";
export const SETS_ROUTE = "/sets";
export const BIBLIOGRAPHY_ROUTE = "/bibliography";
export const COMMENTARY_ROUTE = "/commentary";
export const CONTRIBUTORS_ROUTE = "/contributors";
export const CORRECTIONS_ROUTE = "/corrections";

export const INVENTORY_ROUTE_BY_COMPOSER = `${INVENTORY_ROUTE}/composer`;
export const INVENTORY_ROUTE_ALPHABETICAL = `${INVENTORY_ROUTE}/alphabetical`;
export const COMMENTARY_ROUTE_PRIVATE = `${COMMENTARY_ROUTE}/private`;

export const isActive = (hashPath, route) =>
{
    if (hashPath.startsWith('#'))
    {
        hashPath = hashPath.substr(1);
    }

    return matchPath(hashPath, {path: route, exact: true}) !== null;
};

export default (
    <Switch>
        <App>
            <Route exact path={ ROOT_ROUTE } component={ Description } />
            <Route exact path={ INVENTORY_ROUTE } component={ InventoryByOrder } />
            <Route path={ INVENTORY_ROUTE_BY_COMPOSER } component={ InventoryByComposer } />
            <Route path={ INVENTORY_ROUTE_ALPHABETICAL } component={ InventoryAlphabetical } />
            <Route path={ IMAGES_ROUTE } component={ Images } />
            <Route path={ SETS_ROUTE } component={ Sets } />
            <Route path={ BIBLIOGRAPHY_ROUTE } component={ Bibliography } />
            <Route path={ CONTRIBUTORS_ROUTE } component={ Contributors } />
            <Route path={ COMMENTARY_ROUTE } component={ CommentaryPublic } />
            <Route path={ COMMENTARY_ROUTE_PRIVATE } component={ CommentaryPrivate } />
            <Route path={ CORRECTIONS_ROUTE } component={ Corrections } />
        </App>
    </Switch>
);
