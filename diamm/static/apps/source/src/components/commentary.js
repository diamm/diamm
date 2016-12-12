import React from "react";
import { connect } from "react-redux";
import {
    fetchCommentary
} from "../actions/commentary"

const Comment = ({comment}) =>
{
    return (
        <div>
            { comment.comment }, { comment.author }
        </div>
    )
};


class Commentary extends React.Component
{
    componentDidMount ()
    {
        this.props.fetchCommentary(115, 'source');
    }

    render ()
    {
        return (
            <div className="row">
                <div className="ten columns">
                    <h4>Public comments</h4>
                    { this.props.publicComments.map( (comment, idx) =>
                    {
                        return <Comment comment={ comment } key={ idx } />
                    })}
                </div>
                <div className="six columns">
                    <h4>Private comments</h4>
                    { this.props.privateComments.map( (comment, idx) =>
                    {
                        return (
                            <Comment comment={ comment } key={ idx } />
                        );
                    })}
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        publicComments: state.commentary.public,
        privateComments: state.commentary.private
    }
}

const mapDispatchToProps = {
    fetchCommentary
};

export default connect(mapStateToProps, mapDispatchToProps)(Commentary);
