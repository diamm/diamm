import {
    IIIF_MANIFEST_DID_LOAD
} from "../constants";

const INITIAL_STATE = null;

export default function manifestReducer (state=INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (IIIF_MANIFEST_DID_LOAD):
            return action.manifest;
        default:
            return state;
    }
}
