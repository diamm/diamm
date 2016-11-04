import * as React from "react";

import SearchBox from "../components/searchbox";
import SearchResults from "../components/searchresults";
import SearchFacets from "../components/searchfacets";

interface ISearchProps
{
    children?: any;
}

export default function Search ({
    children = null
}: ISearchProps)
{
    return (
        <div id="search-body-container">
            <SearchBox />
            <SearchResults />
            <SearchFacets />
        </div>
    );
}
