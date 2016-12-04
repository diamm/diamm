import React from "react";
import { connect } from "react-redux";
import {
    updateCurrentQueryTerm
} from "../actions/index";
// import URLSearchParams from "url-search-params";


class SearchBar extends React.Component
{
    static contextTypes = {
        router: React.PropTypes.object
    };

    componentDidMount ()
    {
        // set the search box value in a way that does not trigger the onChange
        // event.
        let params = new URLSearchParams(window.location.search);
        let value = params.get('q') || "";

        this.refs.search_input.value = value;
        this.props.updateCurrentQueryTerm(value);

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
                        ref="search_input"
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
