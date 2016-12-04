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
            <div>
                <div className="search-result-count">
                    { this.props.count } results found.
                </div>
                <div className="search-result-clear">
                    <a onClick={ () => { this.props.clearAll() } }>
                        Clear Search
                    </a>
                </div>
            </div>
        );
    }
}

export default connect(null, { clearAll })(ResultCount);
