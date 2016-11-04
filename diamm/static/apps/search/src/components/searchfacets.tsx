import * as React from 'react';


interface ISearchFacetsProps
{
    children?: any;
}


export default function SearchFacets ({
    children=null
}: ISearchFacetsProps)
{
    return (
        <div id="search-facets">
            <p>Search facets</p>
        </div>
    )
}
