import {
    SET_ACTIVE_TAB,
    INITIALIZE_INVENTORY_DETAIL_STATE,
    SHOW_INVENTORY_DETAILS_FOR_ITEM,
    SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM,
    INITIALIZE_ALPHA_INVENTORY_DETAIL_STATE
} from "../constants";

const INITIAL_STATE = {
    activeTab: null,
    showInventoryDetail: null,
    showAlphaInventoryDetail: null
};

export default function (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case SET_ACTIVE_TAB:
            return { ...state, activeTab: action.tab };
        case INITIALIZE_INVENTORY_DETAIL_STATE:
            return { ...state, showInventoryDetail: new Array(action.payload).fill(false)};
        case INITIALIZE_ALPHA_INVENTORY_DETAIL_STATE:
            return { ...state, showAlphaInventoryDetail: new Array(action.payload).fill(false)};
        case SHOW_INVENTORY_DETAILS_FOR_ITEM:
            return {
                ...state,
                showInventoryDetail: [
                    ...state.showInventoryDetail.slice(0, action.index),
                    state.showInventoryDetail[action.index] === false,  // toggle true / false
                    ...state.showInventoryDetail.slice(action.index + 1)
                ]
            };
        case SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM:
            return {
                ...state,
                showInventoryDetail: [
                    ...state.showAlphaInventoryDetail.slice(0, action.index),
                    state.showAlphaInventoryDetail[action.index] === false,  // toggle true / false
                    ...state.showAlphaInventoryDetail.slice(action.index + 1)
                ]
            };
        default:
            return state;
    }
}
