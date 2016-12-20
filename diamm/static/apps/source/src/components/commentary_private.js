import React from "react";
import { connect } from "react-redux";
import Commentary from "./commentary";
import { Comments } from "./containers/commentary";
import {
    updatePrivateCommentText,
    postComment
} from "../actions/commentary";


class CommentaryPrivate extends React.Component
{
    render ()
    {
        return (
            <Commentary
                commentaryType="private"
                onSubmitButtonClicked={ this.props.postComment }
                commentText={ this.props.privateComment }
                onCommentTextInput={ this.props.updatePrivateCommentText }
            >
                <div className="notification is-warning">Comments made here will only be visible to you.</div>
                <Comments
                    comments={ this.props.privateComments }
                />
            </Commentary>
        );
    }
}

function mapStateToProps (state)
{
    return {
        privateComments: state.commentary.private,
        privateComment: state.commentary.privateComment,
        sourceId: state.source.pk
    }
}

const mapDispatchToProps = {
    updatePrivateCommentText,
    postComment
};

export default connect(mapStateToProps, mapDispatchToProps)(CommentaryPrivate);
