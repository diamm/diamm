import React from "react";
import { connect } from "react-redux";
import AutocompleteComponent from "./autocomplete_component";
import {
    updateCurrentComposerValue,
    performComposerSearch
} from "../actions/facets";
import _ from "lodash";


class ComposerAutocompleteComponent extends React.Component
{
    componentDidMount ()
    {
        let params = new URLSearchParams(window.location.search);
        let composer = params.get('composers_ss') || "";

        this.props.updateCurrentComposerValue(composer);
        this.refs.composer_autocomplete.refs.input.value = composer;
        // this.refs.composer_autocomplete.index.value = composer;
    }

    render ()
    {
        return (
            <Autocomplete
                value={ this.props.currentValue }
                items={ this.props.facets }
                getItemValue={ (item) => item[0] }
                shouldItemRender={ (state, value) => {
                    return state[0].toLowerCase().indexOf(value.toLowerCase()) !== -1
                }}
                onChange={ (event, value) => this.props.updateCurrentValue(value) }
                onSelect={ (value) => this.props.selectCurrentValue(value) }
                renderItem={ (item, isHighlighted) =>
                {
                    return (<div className={ isHighlighted ? "highlighted" : ""}>{ item[0] }</div>);
                }}
                inputProps={ {placeholder: "Search composers"} }
                wrapperStyle={ {} }
                ref="composer_autocomplete"
            />
        );
    }
}


class ComposerFacet extends React.Component
{
    updateCurrentValue (value)
    {
        this.props.updateCurrentComposerValue(value);
    }

    selectCurrentValue (value)
    {
        this.props.updateCurrentComposerValue(value);
        this.props.performComposerSearch(value);
    }

    render ()
    {
        if (_.isEmpty(this.props.composersFacets))
            return null;

        let facets = _.chunk(this.props.composersFacets, 2);

        return (
            <div className="facet-block">
                <div className="facet-title">
                    <h4>Composers</h4>
                </div>
                <div className="facet-body">
                    <AutocompleteComponent
                        value={ this.props.currentValue }
                        items={ facets }
                        updateCurrentValue={ this.updateCurrentValue.bind(this) }
                        selectCurrentValue={ this.selectCurrentValue.bind(this) }
                        placeholder={ "Search composers" }
                    />
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        currentValue: state.currentFacets.composers.facetValue,
        composersFacets: state.results.facets.composers
    }
}

export default connect(mapStateToProps, { updateCurrentComposerValue, performComposerSearch })(ComposerFacet);
