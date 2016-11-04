import * as React from 'react';
import SearchResult from './searchresult';

interface ISearchResultsProps
{
    children?: any;
}

export default function SearchResults ({
    children=null
}: ISearchResultsProps)
{
    return (
        <div id="search-results">
            <p>Search Results</p>
            { children }
        </div>
    )
}
