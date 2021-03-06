import React from "react";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import PropTypes from "prop-types";
import moment from "moment";

import {
    COMMENTARY_ROUTE,
    COMMENTARY_ROUTE_PRIVATE,
    isActive
} from "../../routes";

const CommentaryMenuItem = ({active, route, title, show=true}) =>
{
    if (!show)
        return null;

    return (
        <li className={ active ? 'is-active' : ""}>
            <Link to={ route }>{ title }</Link>
        </li>
    );

};

export class CommentaryMenu extends React.Component
{
    static contextTypes = {
        router: PropTypes.object
    };

    render ()
    {
        return (
            <div className="tabs">
                <ul>
                    <CommentaryMenuItem
                        active={ isActive(this.props.location.hash, COMMENTARY_ROUTE) }
                        route={ COMMENTARY_ROUTE }
                        title="Public Comments"
                    />
                    <CommentaryMenuItem
                        active={ isActive(this.props.location.hash, COMMENTARY_ROUTE_PRIVATE) }
                        route={ COMMENTARY_ROUTE_PRIVATE }
                        title="Private Comments"
                        show={ this.props.isAuthenticated }
                    />
                </ul>
            </div>
        );
    }
}

const Comment = ({comment}) =>
{
    return (
        <article className="media box">
            <div className="media-content">
                <h3 className="title is-5">
                    <span>{ comment.author } </span>
                    { comment.author_is_staff && <span className="tag is-small is-primary">DIAMM Staff</span>}
                </h3>
                <h4 className="subtitle is-6">{ moment(comment.created, "YYYY-MM-DD HH-mm-ss.SSSSSSZ").format("dddd, Do MMMM, YYYY, HH:MM:ss") }</h4>
                <ReactMarkdown source={ comment.comment } />
            </div>
        </article>
    )
};

export const Comments = ({comments}) =>
{
    if (comments.length === 0)
    {
        return (
            <div className="notification">
                <p>No comments have been made.</p>
            </div>
        );
    }
    return (
        <div className="content">
            { comments.map( (comment, idx) =>
            {
                return (
                    <Comment comment={ comment } key={ idx } />
                );
            })}
        </div>
    );
};
