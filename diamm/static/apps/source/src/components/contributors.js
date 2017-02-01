import React from "react";
import { connect } from "react-redux";
import dateFormat from "dateformat";
import {
    fetchContributors
} from "../actions/contributors";


class Contributors extends React.Component
{
    componentDidMount ()
    {
        this.props.fetchContributors(this.props.sourceId, 'source');
    }

    render ()
    {
        if (!this.props.contributors || this.props.contributors.results.length === 0)
        {
            return (
                <div className="columns">
                    <div className="column">
                        <div className="notification">
                            No contributors to show for this record.
                        </div>
                    </div>
                </div>
            );
        }
        return (
            <div className="columns">
                <div className="column is-8">
                    { this.props.contributors.results.map( (entry, idx) =>
                    {
                        let contributor = entry.contributor || entry.credit;
                        return (
                            <div key={ idx } className="media">
                                <div className="media-content">
                                    <div className="content">
                                        <h3 className="title is-5"><span>{ contributor }</span></h3>
                                        <h4 className="subtitle is-6">{ dateFormat(entry.updated, "dddd, mmmm dS, yyyy, h:MM:ss TT") }</h4>
                                        <p>{ entry.summary }</p>
                                    </div>
                                </div>
                            </div>
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
        sourceId: state.source.pk,
        contributors: state.contributors
    };
}

export default connect(mapStateToProps, { fetchContributors })(Contributors);
