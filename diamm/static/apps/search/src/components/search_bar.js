import React from "react";
import { connect } from "react-redux";
import {
    updateCurrentQueryTerm,
    performSearch
} from "../actions/index";


class SearchBar extends React.Component
{
    static contextTypes = {
        router: React.PropTypes.object
    };

    componentWillMount ()
    {
        if (this.props.defaultQuery.q)
        {
            this.props.updateCurrentQueryTerm(this.props.defaultQuery.q);
            this.props.onSearchTermChange(this.props.defaultQuery.q);
        }

    }

    onInputChange (event)
    {
        this.props.updateCurrentQueryTerm(event.target.value);
        this.props.onSearchTermChange(event.target.value);
    }

    render ()
    {
        return (
            <div className="row">
                <div className="sixteen columns search-box">
                    <input
                        type="text"
                        placeholder="Search"
                        value={ this.props.currentQuery }
                        onChange={ event => this.onInputChange(event) }
                    />
                </div>
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        currentQuery: state.currentQuery
    };
}

export default connect(mapStateToProps, { updateCurrentQueryTerm })(SearchBar);
