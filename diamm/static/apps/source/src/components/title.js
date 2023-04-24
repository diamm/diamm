import React from "react";
import { connect } from "react-redux";


class Title extends React.Component
{
    render ()
    {
        const { archive } = this.props;

        return (
            <div id="source-heading" className="columns">
                <div className="column is-two-thirds">
                    <h2 className="title is-3">{ this.props.display_name }</h2>
                    <h3 className="subtitle is-5" style={ { marginBottom: "0.5rem" } }>
                        <a href={ archive.url }>{ archive.name }</a>, <span>{ archive.city }, { archive.country }</span>
                    </h3>
                    <h4 className="subtitle is-6">{ this.props.source_type ? `${this.props.source_type}`: '' }{ this.props.date_statement ? `, ${this.props.date_statement}` : '' }</h4>
                </div>
                <div className="column source-archive-logo">
                    <a href={ archive.url }>
                        <img src={ archive.logo } className="archive-header-logo"/>
                    </a>
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        display_name: state.source.display_name,
        archive: state.source.archive,
        source_type: state.source.source_type,
        date_statement: state.source.date_statement
    };
}

export default connect(mapStateToProps)(Title);
