import React from "react";
import { connect } from "react-redux";


class Title extends React.Component
{
    render ()
    {
        const { archive } = this.props;

        return (
            <div id="source-heading" className="columns">
                <div className="column is-10 source-header">
                    <h1 className="title is-2">{ this.props.display_name }</h1>
                    <h2 className="subtitle is-4" style={ {marginBottom: "10px"} }>
                        <a href={ archive.url }>{ archive.name }</a>, <span>{ archive.city }, { archive.country }</span>
                    </h2>
                    <h3 className="subtitle is-5">{ this.props.source_type }, { this.props.date_statement }</h3>
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
