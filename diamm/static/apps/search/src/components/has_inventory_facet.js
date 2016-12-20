import React from "react";
import { connect } from "react-redux";
import Facet from "./facets";
import _ from "lodash";
import {
    performHasInventorySearch,
    updateHasInventoryValue,
    clearHasInventoryValue
} from "../actions/has_inventory_facet";


class HasInventoryFacet extends React.Component
{
    selectHasInventoryValue (value)
    {
        this.props.updateHasInventoryValue(value);
        this.props.performHasInventorySearch();
    }

    clearHasInventory ()
    {
        this.props.clearHasInventoryValue();
        this.props.performHasInventorySearch();
    }

    _showControls ()
    {
        return (
            <div
                className="facet-show-control"
                onClick={ () => this.clearHasInventory() }
            >
                Clear
            </div>
        )
    }

    render ()
    {
        let facets = _.chunk(this.props.hasInventoryFacet, 2);
        return (
            <Facet
                title="Has Inventory"
                bodyClasses={ 'select-list' }
                controls={ this._showControls() }
            >
                { facets.map( (facet, idx) =>
                {
                    return (
                        <div key={ idx }>
                            <label>
                                <input
                                    type="radio"
                                    name="has-inventory"
                                    checked={ this.props.activeSelect === facet[0] }
                                    onChange={ () => this.selectHasInventoryValue(facet[0])}
                                />
                                { facet[0] === "true" ? "Yes" : "No" }
                            </label>
                        </div>
                    );
                })}
            </Facet>
        );
    }
}

function mapStateToProps (state)
{
    return {
        hasInventoryFacet: state.results.facets.has_inventory,
        activeSelect: state.currentFacets.hasInventory.active
    };
}

const mapDispatchToProps = {
    performHasInventorySearch,
    updateHasInventoryValue,
    clearHasInventoryValue
};

export default connect(mapStateToProps, mapDispatchToProps)(HasInventoryFacet);
