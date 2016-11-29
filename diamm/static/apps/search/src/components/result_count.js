import React from "react";
import { connect } from "react-redux";


class ResultCount extends React.Component
{
    render ()
    {
        return (
            <div className="search-result-count">
                { this.props.count } results found.
            </div>
        );
    }
}

export default ResultCount;
