import React from "react";
import debounce from "lodash.debounce";
import { connect } from "react-redux";
import {
    performInitialPageLoadSearch,
    performQueryTermSearch
} from "../actions/index";
import {
    performSearch
} from "../actions/search_api";
// import URLSearchParams from "url-search-params";
// import "babel-polyfill";

import SearchBar from "./search_bar";
import SearchTypeFilter from "./search_type_filter";
import SideBar from "./side_bar";
import Results from "./results";

class App extends React.Component
{
    componentDidMount ()
    {
        this.props.performInitialPageLoadSearch();
    }

    render ()
    {
        if (!this.props.results)
        {
            return null;
        }

        /*
         * Cause a search query to fire only once every 500ms, so that we don't overload the server
         * handling every keypress.
         * */
        const searchTermChange = debounce(
            (term) => {
                this.props.performQueryTermSearch(term);
            }, 800);

        return (
            <div>
                <SearchBar
                    defaultQuery={ this.props.location.query }
                    onSearchTermChange={ searchTermChange }
                />
                <SearchTypeFilter />
                <div className="container">
                    <div className="row">
                        <div className="three columns">
                            <SideBar />
                        </div>
                        <div className="thirteen columns">
                            <Results
                                results={ this.props.results }
                            />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        results: state.results
    }
}

export default connect(mapStateToProps, { performInitialPageLoadSearch, performQueryTermSearch })(App);
