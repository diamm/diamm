import {
    UPDATE_COMMENTARY
} from "../constants";


const INITIAL_STATE = {
    public: [],
    private: []
};

export default function commentaryReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_COMMENTARY):
            return { ...state, public: action.public, private: action.private };
        default:
            return state;
    }
}
