import React from "react";
import { connect } from "react-redux";


class SearchTypeFilter extends React.Component
{
    render ()
    {
        return (
            <div className="row type-filter">

            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {};
}

export default connect(mapStateToProps)(SearchTypeFilter);
