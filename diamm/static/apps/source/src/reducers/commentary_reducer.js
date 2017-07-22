import {
    UPDATE_COMMENTARY,
    UPDATE_PRIVATE_COMMENT_TEXT,
    UPDATE_PUBLIC_COMMENT_TEXT,
    CLEAR_PRIVATE_COMMENT_TEXT,
    CLEAR_PUBLIC_COMMENT_TEXT,
    COMMENT_SUBMITTING,
    COMMENT_SUBMITTED
} from "../constants";


const INITIAL_STATE = {
    public: [],
    private: [],
    publicComment: "",
    privateComment: "",
    submitted: false,
    submitting: false
};

export default function commentaryReducer (state = INITIAL_STATE, action)
{
    switch (action.type)
    {
        case (UPDATE_COMMENTARY):
            return { ...state, public: action.public, private: action.private };
        case (UPDATE_PRIVATE_COMMENT_TEXT):
            return { ...state, privateComment: action.text };
        case (UPDATE_PUBLIC_COMMENT_TEXT):
            return { ...state, publicComment: action.text };
        case (CLEAR_PRIVATE_COMMENT_TEXT):
            return { ...state, privateComment: "" };
        case (CLEAR_PUBLIC_COMMENT_TEXT):
            return { ...state, publicComment: "" };
        case (COMMENT_SUBMITTING):
            return { ...state, submitting: true };
        case (COMMENT_SUBMITTED):
            return { ...state, submitting: false, submitted: true};
        default:
            return state;
    }
}
