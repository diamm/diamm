import React from "react";
import { connect } from "react-redux";
import Result from "./result";
import "url-search-params";
import ReactPaginate from 'react-paginate';
import {
    performSearch
} from "../actions/search_api";

class Results extends React.Component
{
    handlePaginationClick ({selected})
    {
        let page = selected + 1;
        let params = new URLSearchParams(window.location.search);
        params.set('page', page);

        let qstring = params.toString();

        this.props.performSearch(qstring);
    }

    render ()
    {
        if (!this.props.results)
        {
            return null;
        }

        if (this.props.count === 0)
        {
            return (
                <div className="search-results">
                    <p>No results</p>
                </div>
            )
        }

        return (
            <div className="search-results">
                { this.props.results.map( (result) => {
                    return <Result result={ result } key={ result.id } />
                })}
                <nav className="pagination">
                    <ReactPaginate
                        pageNum={ this.props.pagination.num_pages }
                        pageRangeDisplayed={ 5 }
                        marginPagesDisplayed={ 4 }
                        clickCallback={ this.handlePaginationClick.bind(this) }
                        containerClassName="pagination-list"
                        nextLabel={ "\u00BB" }
                        previousLabel={ "\u00AB" }
                        nextLinkClassName="pagination-next"
                        previousLinkClassName="pagination-previous"
                        breakClassName="pagination-ellipsis"
                        pageLinkClassName="pagination-link"
                        disabledClassName="is-disabled"
                        activeClassName="is-current"
                    />
                </nav>
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        results: state.results.results,
        pagination: state.results.pagination,
        count: state.results.count
    };
}

export default connect(mapStateToProps, { performSearch })(Results);
