import React from "react";
import { Route, IndexRoute } from "react-router";
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
import Credits from "./components/credits";

export const ROOT_ROUTE = "/";
export const INVENTORY_ROUTE = "inventory";
export const IMAGES_ROUTE = "images";
export const SETS_ROUTE = "sets";
export const BIBLIOGRAPHY_ROUTE = "bibliography";
export const COMMENTARY_ROUTE = "commentary";
export const CREDITS_ROUTE = "credits";

export const INVENTORY_ROUTE_BY_COMPOSER = `${INVENTORY_ROUTE}/composer`;
export const INVENTORY_ROUTE_ALPHABETICAL = `${INVENTORY_ROUTE}/alphabetical`;
export const COMMENTARY_ROUTE_PRIVATE = `${COMMENTARY_ROUTE}/private`;


export default (
    <Route path={ ROOT_ROUTE } component={ App }>
        <IndexRoute component={ Description } />
        <Route path={ INVENTORY_ROUTE } component={ InventoryByOrder } />
        <Route path={ INVENTORY_ROUTE_BY_COMPOSER } component={ InventoryByComposer } />
        <Route path={ INVENTORY_ROUTE_ALPHABETICAL } component={ InventoryAlphabetical } />
        <Route path={ IMAGES_ROUTE } component={ Images } />
        <Route path={ SETS_ROUTE } component={ Sets } />
        <Route path={ BIBLIOGRAPHY_ROUTE } component={ Bibliography } />
        <Route path={ CREDITS_ROUTE } component={ Credits } />
        <Route path={ COMMENTARY_ROUTE } component={ CommentaryPublic } />
        <Route path={ COMMENTARY_ROUTE_PRIVATE } component={ CommentaryPrivate } />
    </Route>
);
