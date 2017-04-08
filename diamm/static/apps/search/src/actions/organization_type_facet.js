import {
    ADD_ORGANIZATION_TYPE_TO_ACTIVE,
    REMOVE_ORGANIZATION_TYPE_FROM_ACTIVE,
    CLEAR_ACTIVE_ORGANIZATION_TYPES
} from "../constants";

import {
    performSearch
} from "./search_api";


export function addOrganizationToActive (value)
{
    return {
        type: ADD_ORGANIZATION_TYPE_TO_ACTIVE,
        value
    }
}

export function removeOrganizationFromActive (value) {
    return {
        type: REMOVE_ORGANIZATION_TYPE_FROM_ACTIVE,
        value
    }
}

export function clearActiveOrganizations() {
    return {
        type: CLEAR_ACTIVE_ORGANIZATION_TYPES
    }
}

export function performOrganizationTypeSearch ()
{
    return (dispatch, getState) =>
    {
        let currentState = getState();
        let activeOrganizations = currentState.currentFacets.organizationTypes.active;

        let params = new URLSearchParams(window.location.search);
        params.delete('orgtype');
        activeOrganizations.map( (p) => params.append('orgtype', p));
        let qstring = params.toString();

        dispatch(
            performSearch(qstring)
        )
    }
}