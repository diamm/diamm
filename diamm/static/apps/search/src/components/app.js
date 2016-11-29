import React from "react";
import debounce from "lodash.debounce";
import { connect } from "react-redux";
import { performSearch } from "../actions/index";
import SearchBar from "./search_bar";
import SearchTypeFilter from "./search_type_filter";
import SideBar from "./side_bar";
import Results from "./results";

class App extends React.Component
{
    componentDidMount ()
    {
        console.log(this.props.location.query);
    }

    render ()
    {
        /*
         * Cause a search query to fire only once every 500ms, so that we don't overload the server
         * handling every keypress.
         * */
        const searchTermChange = debounce( (term) => { this.props.dispatch(performSearch(term)) }, 500);
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
                            <Results />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default connect()(App);
