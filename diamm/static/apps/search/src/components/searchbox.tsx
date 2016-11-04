import * as React from 'react';
import SearchTypeFilter from './searchtypefilter';


interface ISearchBoxProps
{
    children?: any;
}

export default function SearchBox ({
    children=null
}: ISearchBoxProps)
{
    return (
        <div id="search-box">
            <p>Searchbox</p>
            <SearchTypeFilter />
        </div>
    )
}
