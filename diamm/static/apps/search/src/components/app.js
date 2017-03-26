import React from "react";
import debounce from "lodash.debounce";
import { connect } from "react-redux";
import {
    performInitialPageLoadSearch,
    performQueryTermSearch
} from "../actions/index";

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
                <div className="columns container is-fluid">
                    <div className="column is-one-quarter">
                        <SideBar />
                    </div>
                    <div className="column is-three-quarters">
                        <Results
                            results={ this.props.results }
                        />
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
