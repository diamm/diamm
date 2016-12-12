import React from "react";
import { connect } from "react-redux";
import {
    performTypeFacetQuery,
    setActiveTypeFacet
} from "../actions/facets";
// import URLSearchParams from "url-search-params";


class SearchTypeFilter extends React.Component
{
    componentDidMount ()
    {
        let params = new URLSearchParams(window.location.search);
        let type = params.get('type') || "";
        if (type)
            this.props.setActiveTypeFacet(type);
    }

    handleTypeClick (type)
    {
        this.props.performTypeFacetQuery(type);
        this.props.setActiveTypeFacet(type);
    }

    render ()
    {
        let sortedKeys = Object.keys(this.props.types);
        sortedKeys.sort();

        return (
            <div className="columns type-filter">
                <div className="type-filter-label">
                    Filter:
                </div>
                <div className={ ("all" === this.props.currentQueryType) ? "show-all active" : "show-all" }>
                    <a onClick={ () => this.handleTypeClick("all") }>
                        Show All
                    </a>
                </div>
                <ul>
                { sortedKeys.map( (typ, idx) =>
                {
                    let classes = (typ === this.props.currentQueryType) ? "type-filter-facet active" : "type-filter-facet";
                    return (
                        <li key={ idx } className={ classes }>
                            <a onClick={ () => this.handleTypeClick(typ) }>
                                { typ.split("_").join(" ") } ({ this.props.types[typ] })
                            </a>
                        </li>
                    );
                })}
                </ul>
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        types: state.results.types,
        count: state.results.count,
        currentQueryType: state.currentQueryType
    };
}

export default connect(mapStateToProps, { performTypeFacetQuery, setActiveTypeFacet })(SearchTypeFilter);
