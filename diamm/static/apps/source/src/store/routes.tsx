import * as React from "react";
import { IndexRoute, Route } from "react-router";

import Source from "../components/source";
import Inventory from "../components/inventory";
import Description from "../components/description";
import Images from "../components/images";
import Bibliography from "../components/bibliography";
import Sets from "../components/sets";

export default (
    <Route path="/" component={ Source }>
        <Route path="inventory" component={ Inventory } />
        <Route path="images" component={ Images } />
        <Route path="sets" component={ Sets } />
        <Route path="bibliography" component={ Bibliography } />
    </Route>
);
