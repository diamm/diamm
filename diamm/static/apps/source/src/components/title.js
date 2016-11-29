import React from "react";
import { connect } from "react-redux";


class Title extends React.Component
{
    render ()
    {
        const { archive } = this.props;

        return (
            <div id="source-heading" className="row">
                <div className="twelve columns source-header">
                    <h1>{ this.props.display_name }</h1>
                    <h2>
                        <a href={ archive.url }>{ archive.name }</a>, <span>{ archive.city }, { archive.country }</span>
                    </h2>
                    <div>{ this.props.type }, { this.props.date_statement }</div>
                </div>
                <div className="four columns source-archive-logo">
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
        type: state.source.source_type,
        date_statement: state.source.date_statement
    };
}

export default connect(mapStateToProps)(Title);
