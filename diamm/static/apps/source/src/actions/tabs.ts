import { SWITCH_TAB } from "../constants";


export function switchToTab (tabId: string)
{
    return {
        type: SWITCH_TAB,
        tabId
    };
}
