import React from "react";
import { connect } from "react-redux";

import {
    clearAll
} from "../actions";

class ResultCount extends React.Component
{
    render ()
    {
        return (
            <div className="search-results-info">
                <div className="search-result-count">
                    { this.props.count } results found.
                </div>
                <button onClick={ () => { this.props.clearAll() } } className="button is-primary">
                    Clear Search
                </button>
            </div>
        );
    }
}

export default connect(null, { clearAll })(ResultCount);
