import React from "react";
import { connect } from "react-redux";
import AutocompleteComponent from "./autocomplete_component";
import Facet from "./facets";
import {
    updateCurrentComposerValue,
    performComposerSearch,
    addComposerToActive,
    clearActiveComposers,
    removeComposerFromActive
} from "../actions/facets";
import _ from "lodash";


// class ComposerAutocompleteComponent extends React.Component
// {
//     componentDidMount ()
//     {
//         let params = new URLSearchParams(window.location.search);
//         let composer = params.get('composers_ss') || "";
//
//         this.props.updateCurrentComposerValue(composer);
//         this.refs.composer_autocomplete.refs.input.value = composer;
//         // this.refs.composer_autocomplete.index.value = composer;
//     }
// }


class ComposerFacet extends React.Component
{
    updateCurrentValue (value)
    {
        this.props.updateCurrentComposerValue(value);
    }

    selectCurrentValue (value)
    {
        // reset the state key to a blank value.
        this.props.updateCurrentComposerValue("");
        // shift the selected value to the 'active' keys
        this.props.addComposerToActive(value);
        // fire off a search.
        this.props.performComposerSearch();
    }

    removeComposerFromActive (value)
    {
        this.props.removeComposerFromActive(value);
        this.props.performComposerSearch();
    }

    resetFacet ()
    {
        this.props.clearActiveComposers();
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
        if (_.isEmpty(this.props.composersFacets))
            return null;

        let facets = _.chunk(this.props.composersFacets, 2);

        return (
            <div>
                <Facet
                    title="Composers"
                    controls={ this._showControls() }
                >
                    <AutocompleteComponent
                        value={ this.props.currentValue }
                        items={ facets }
                        updateCurrentValue={ this.updateCurrentValue.bind(this) }
                        selectCurrentValue={ this.selectCurrentValue.bind(this) }
                        placeholder={ "Search composers" }
                    />
                </Facet>
                <div className="selected-composers">
                    { this.props.activeValues.map( (c, idx) =>
                    {
                        return (
                            <div className="selected-autocomplete-facet" key={ idx }>
                                <span>{ c }</span>
                                <i
                                    className="fa fa-close"
                                    onClick={ () => this.removeComposerFromActive(c) }
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
        currentValue: state.currentFacets.composers.facetValue,
        activeValues: state.currentFacets.composers.active,
        composersFacets: state.results.facets.composers
    }
}

const mapDispatchToProps = {
    updateCurrentComposerValue,
    performComposerSearch,
    addComposerToActive,
    clearActiveComposers,
    removeComposerFromActive
};

export default connect(mapStateToProps, mapDispatchToProps)(ComposerFacet);
