import React from "react";
import { connect } from "react-redux";
import Commentary from "./commentary";
import { Comments } from "./containers/commentary"
import {
    updatePublicCommentText,
    postComment
} from "../actions/commentary";

class CommentaryPublic extends React.Component
{
    render ()
    {
        return (
            <Commentary
                commentaryType="public"
                onSubmitButtonClicked={ this.props.postComment }
                commentText={ this.props.publicComment }
                onCommentTextInput={ this.props.updatePublicCommentText }
            >
                <Comments
                    comments={ this.props.publicComments }
                />
            </Commentary>
        );
    }
}

function mapStateToProps (state)
{
    return {
        publicComments: state.commentary.public,
        publicComment: state.commentary.publicComment
    }
}

const mapDispatchToProps = {
    updatePublicCommentText,
    postComment
};
export default connect(mapStateToProps, mapDispatchToProps)(CommentaryPublic);
