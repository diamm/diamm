import React from "react";
import { connect } from "react-redux";
import AutocompleteComponent from "./autocomplete_component";
import Facet from "./facets";
import {
    addNotationToActive,
    removeNotationFromActive,
    clearActiveNotations,
    updateCurrentNotationValue,
    performNotationSearch
} from "../actions/notations_facet";


class NotationsFacet extends React.Component
{
    updateCurrentValue (value)
    {
        this.props.updateCurrentNotationValue(value);
    }

    selectCurrentValue (value)
    {
        this.props.updateCurrentNotationValue("");
        this.props.addNotationToActive(value);
        this.props.performNotationSearch();

    }

    removeNotationFromActive (value)
    {
        this.props.removeNotationFromActive(value);
        this.props.performNotationSearch();
    }

    resetFacet ()
    {
        this.props.clearActiveNotations();
        this.props.performNotationSearch();
    }

    _showControls ()
    {
        return (
            <div className="facet-show-control" onClick={ () => this.resetFacet() }>
                Clear all
            </div>
        );
    }

    render ()
    {
        let facets = _.chunk(this.props.notationsFacets, 2);

        return (
            <div>
                <Facet
                    title="Notations"
                    controls={ this._showControls() }
                >
                    <AutocompleteComponent
                        value= { this.props.currentValue }
                        items={ facets }
                        updateCurrentValue={ this.updateCurrentValue.bind(this) }
                        selectCurrentValue={ this.selectCurrentValue.bind(this) }
                        placeholder={ "Search notations" }/>
                </Facet>
                <div className="selected-notations">
                    { this.props.activeValues.map( (n, idx) =>
                    {
                        return (
                            <div className="selected-autocomplete-facet" key={ idx }>
                                <span>{ n }</span>
                                <i
                                    className="fa fa-close"
                                    onClick={ () => this.removeNotationFromActive(n) }
                                />
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        currentValue: state.currentFacets.notations.facetValue,
        activeValues: state.currentFacets.notations.active,
        notationsFacets: state.results.facets.notations
    };
}

const mapDispatchToProps = {
    addNotationToActive,
    removeNotationFromActive,
    clearActiveNotations,
    updateCurrentNotationValue,
    performNotationSearch
};

export default connect(mapStateToProps, mapDispatchToProps)(NotationsFacet);
