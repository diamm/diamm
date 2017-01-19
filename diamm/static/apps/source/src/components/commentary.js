import React from "react";
import { connect } from "react-redux";
import {
    fetchCommentary
} from "../actions/commentary"
import {
    CommentaryMenu
} from "./containers/commentary";
import DebounceInput from "react-debounce-input";

/*
* The commentary panel. Users must be logged in to comment, but they
* can see previous comments made without being logged in.
*
* Commentary can be both private and public.
*
* */
class Commentary extends React.Component
{
    componentDidMount ()
    {
        this.props.fetchCommentary(this.props.sourceId, 'source');
    }

    _commentaryEdit ()
    {
        if (!this.props.isAuthenticated)
        {
            return (
                <div className="columns">
                    <div className="column">
                        <div className="notification">
                            You must be logged in to post a comment.
                        </div>
                    </div>
                </div>
            );
        }

        return (
            <div className="columns">
                <hr />
                <div className="column is-8">
                    <h4 className="title is-5">Add a comment</h4>
                    <p className="control">
                        <DebounceInput
                            element="textarea"
                            forceNotifyByEnter={false}
                            minLength={ 2 }
                            debounceTimeout={ 600 }
                            onChange={ event => this.props.onCommentTextInput(event.target.value) }
                            rows="7"
                            value={ this.props.commentText }
                            className="textarea"
                        />
                    </p>
                    <p className="control is-pulled-right">
                        <button
                            className="button is-primary"
                            onClick={ () => this.props.onSubmitButtonClicked(
                                this.props.commentText,
                                this.props.commentaryType,
                                'source',
                                this.props.sourceId)
                            }
                        >
                            Post a { this.props.commentaryType } comment
                        </button>
                    </p>
                </div>
                <div className="column is-3">
                    <p><strong>Markdown formatting is supported</strong></p>
                    <ul>
                        <li><code>**bold**</code>: <strong>bold</strong></li>
                        <li><code>*italic*</code>: <em>italic</em></li>
                        <li><code>[A link](http://example.com)</code>: <a href="http://example.com/">A link</a></li>
                    </ul>
                </div>
            </div>
        );
    }

    render ()
    {
        return (
            <div>
                <div className="columns">
                    <div className="column">
                        <nav className="level">
                            <div className="level-left">
                                <div className="level-item">
                                    <CommentaryMenu isAuthenticated={ this.props.isAuthenticated } />
                                </div>
                            </div>
                        </nav>
                    </div>
                </div>
                <div className="columns">
                    <div className="column">
                        { this.props.children }
                    </div>
                </div>
                { this._commentaryEdit() }
            </div>

        );
    }
}

function mapStateToProps (state)
{
    return {
        publicComments: state.commentary.public,
        privateComments: state.commentary.private,
        sourceId: state.source.pk,
        isAuthenticated: state.user.isAuthenticated
    }
}

const mapDispatchToProps = {
    fetchCommentary
};

export default connect(mapStateToProps, mapDispatchToProps)(Commentary);
