import React from "react";
import { connect } from "react-redux";
import _ from "lodash";
import AutocompleteComponent from "./autocomplete_component";
import Facet from "./facets";
import {
    addSourceTypeToActive,
    removeSourceTypeFromActive,
    clearActiveSourceTypes,
    updateCurrentSourceTypeValue,
    performSourceTypeSearch
} from "../actions/source_type_facet";


class SourceTypeFacet extends React.Component
{
    updateCurrentValue (value)
    {
        this.props.updateCurrentSourceTypeValue(value);
    }

    selectCurrentValue (value)
    {
        this.props.updateCurrentSourceTypeValue("");
        this.props.addSourceTypeToActive(value);
        this.props.performSourceTypeSearch();
    }

    removeSourceTypeFromActive (value)
    {
        this.props.removeSourceTypeFromActive(value);
        this.props.performSourceTypeSearch();
    }

    resetFacet ()
    {
        this.props.clearActiveSourceTypes();
        this.props.performSourceTypeSearch();
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
        let facets = _.chunk(this.props.sourceTypesFacets, 2);

        return (
            <div>
                <Facet
                    title="Source Types"
                    controls={ this._showControls() }
                >
                    <AutocompleteComponent
                        value={ this.props.currentValue }
                        items={ facets }
                        updateCurrentValue={ this.updateCurrentValue.bind(this) }
                        selectCurrentValue={ this.selectCurrentValue.bind(this) }
                        placeholder={ "Search source types" }/>
                </Facet>
                <div className="selected-source-types">
                    { this.props.activeValues.map( (s, idx) =>
                    {
                        return (
                            <div className="selected-autocomplete-facet" key={ idx }>
                                <span>{ s }</span>
                                <i
                                    className="fa fa-close"
                                    onClick={ () => this.removeSourceTypeFromActive(s) }
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
        currentValue: state.currentFacets.sourceTypes.facetValue,
        activeValues: state.currentFacets.sourceTypes.active,
        sourceTypesFacets: state.results.facets.source_type
    };
}

const mapDispatchToProps = {
    addSourceTypeToActive,
    removeSourceTypeFromActive,
    clearActiveSourceTypes,
    updateCurrentSourceTypeValue,
    performSourceTypeSearch
};

export default connect(mapStateToProps, mapDispatchToProps)(SourceTypeFacet);
