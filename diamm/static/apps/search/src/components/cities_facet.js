import React from "react";
import { connect } from "react-redux";
import AutocompleteComponent from "./autocomplete_component";
import Facet from "./facets";
import {
    updateCurrentCitiesValue,
    addCitiesToActive,
    clearActiveCities,
    removeCitiesFromActive,
    performCitiesSearch
} from "../actions/cities_facet";

class CitiesFacet extends React.Component
{
    updateCurrentValue (value)
    {
        this.props.updateCurrentCitiesValue(value);
    }

    selectCurrentValue (value)
    {
        this.props.updateCurrentCitiesValue("");
        this.props.addCitiesToActive(value);
        this.props.performCitiesSearch();
    }

    removeCitiesFromActive (value)
    {
        this.props.removeCitiesFromActive(value);
        this.props.performCitiesSearch();
    }

    resetFacet ()
    {
        this.props.clearActiveCities();
        this.props.performNotationSearch();
    }

    _showControls ()
    {
        return (
            <div className="facet-show-control" onClick={ () => this.resetFacet() }>
                Clear all
            </div>
        )
    }

    render ()
    {
        let facets = _.chunk(this.props.citiesFacet, 2);

        return (
            <div>
                <Facet title="Cities" controls={ this._showControls() }>
                    <AutocompleteComponent value={ this.props.currentValue }
                                           items={ facets }
                                           updateCurrentValue={ this.updateCurrentValue.bind(this) }
                                           selectCurrentValue={ this.selectCurrentValue.bind(this) }
                                           placeholder={ "Search Cities" }/>

                </Facet>
                <div className="selected-cities">
                    { this.props.activeValues.map( (n, idx) => {
                        return (
                            <div className="selected-autocomplete-facet" key={ idx }>
                                <span>{ n }</span>
                                <i className="fa fa-close" onClick={ () => this.removeCitiesFromActive(n) }/>
                            </div>
                        )
                    })}
                </div>
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        currentValue: state.currentFacets.cities.facetValue,
        activeValues: state.currentFacets.cities.active,
        citiesFacet: state.results.facets.cities
    }
}

const mapDispatchToProps = {
    addCitiesToActive,
    removeCitiesFromActive,
    clearActiveCities,
    updateCurrentCitiesValue,
    performCitiesSearch
};

export default connect(mapStateToProps, mapDispatchToProps)(CitiesFacet);