import * as React from 'react';


interface ISearchResultProp
{
    children?: any;
}

export default function SearchResult ({
    children=null
}: ISearchResultProp)
{
    return (
        <div className="search-result">
            <p>Search result</p>
        </div>
    )
}
