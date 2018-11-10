import { combineReducers } from "redux";
import { routerReducer } from "react-router-redux";
import sourceReducer from "./source_reducer";
import userReducer from "./user_reducer";
import tabsReducer from "./tabs_reducer";
import manifestReducer from "./manifest_reducer";
import imageViewReducer from "./image_view_reducer";
import quickLookReducer from "./quicklook_reducer";
import commentaryReducer from "./commentary_reducer";
import correctionsReducer from "./corrections_reducer";
import inventoryReducer from "./inventory_reducer";
import contributorsReducer from "./contributors_reducer";

const rootReducer = combineReducers({
    user: userReducer,
    source: sourceReducer,
    tabs: tabsReducer,
    manifest: manifestReducer,
    image_view: imageViewReducer,
    quicklook: quickLookReducer,
    commentary: commentaryReducer,
    corrections: correctionsReducer,
    inventory: inventoryReducer,
    contributors: contributorsReducer,
    routing: routerReducer
});

export default rootReducer;
