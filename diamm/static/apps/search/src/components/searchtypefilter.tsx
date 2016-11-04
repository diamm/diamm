import * as React from 'react';

interface ISearchTypeFilterProps
{
    children?: any;
}

export default function SearchTypeFacets ({
    children=null
}: ISearchTypeFilterProps)
{
    return (
        <div id="search-type-filter">
            <p>Search type filter</p>
        </div>
    )
}
