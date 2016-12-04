import {
    SERVER_BASE_URL,
    SET_USER_INFO,
    RECEIVE_SOURCE_INFO,
    SET_ACTIVE_TAB,
    INITIALIZE_INVENTORY_DETAIL_STATE,
    SHOW_INVENTORY_DETAILS_FOR_ITEM,
    INITIALIZE_ALPHA_INVENTORY_DETAIL_STATE,
    SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM,
    OPEN_QUICKLOOK_VIEW,
    CLOSE_QUICKLOOK_VIEW
} from "../constants";


export function setUserInfo (username, authenticated, staff, superuser)
{
    const isStaff = staff === "True";
    const isSuperuser = superuser === "True";
    const isAuthenticated = authenticated === "True";

    return {
        type: SET_USER_INFO,
        payload: {
            username,
            isAuthenticated,
            isStaff,
            isSuperuser
        }
    }
}

export function receiveSourceInfo (payload)
{
    return {
        type: RECEIVE_SOURCE_INFO,
        payload
    }
}

export function fetchSourceInfo (sourceId)
{
    return (dispatch) =>
    {
        return fetch(`${SERVER_BASE_URL}sources/${sourceId}/`, {
                headers: {
                    "Accept": "application/json"
                }
            })
            .then((response) => {
                return response.json();
            })
            .then((payload) => {
                dispatch(receiveSourceInfo(payload));
                dispatch(initializeInventoryDetailState(payload.inventory));
                dispatch(initializeAlphaInventoryDetailState(payload.inventory));
            });
    };
}

export function setActiveTab (location)
{
    return {
        type: SET_ACTIVE_TAB,
        tab: location.pathname
    }
}

export function showInventoryDetailsForItem (idx)
{
    return {
        type: SHOW_INVENTORY_DETAILS_FOR_ITEM,
        index: idx
    }
}

export function initializeInventoryDetailState (inventory)
{
    return {
        type: INITIALIZE_INVENTORY_DETAIL_STATE,
        payload: inventory.length
    }
}


export function initializeAlphaInventoryDetailState (inventory)
{
    return {
        type: INITIALIZE_ALPHA_INVENTORY_DETAIL_STATE,
        payload: inventory.length
    }
}

export function showAlphaInventoryDetailsForItem (idx)
{
    return {
        type: SHOW_ALPHA_INVENTORY_DETAILS_FOR_ITEM,
        index: idx
    }
}

export function openQuickLookView (url)
{
    return (dispatch) =>
    {
        return fetch(url, {
            headers: {
                "Accept": "application/json"
            }
        }).then((response) =>
        {
            return response.json()
        }).then((payload) =>
        {
            dispatch({
                type: OPEN_QUICKLOOK_VIEW,
                payload
            })
        })
    }
}

export function closeQuickLookView ()
{
    return {
        type: CLOSE_QUICKLOOK_VIEW
    }
}
