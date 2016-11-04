import { SWITCH_TAB } from "../constants";


// see: https://spin.atomicobject.com/2016/09/27/typed-redux-reducers-typescript-2-0/
export type OtherAction = { type: ""; }
export const OtherAction: OtherAction = { type: "" };


export type SwitchTabAction = {
    type: SWITCH_TAB,
    id: string
}
