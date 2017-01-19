import React from "react";
import Inventory from "./inventory";
import { connect } from "react-redux";
import _ from "lodash";
import { createSelector } from "reselect";

import {
    QuickLook,
    Composers,
    Foliation
} from "./containers/inventory";
import Details from "./inventory_details";
import { showAlphaInventoryDetailsForItem } from "../actions/inventory";

class InventoryAlphabetical extends React.Component
{
    handleShowDetailClick (idx)
    {
        this.props.showAlphaInventoryDetailsForItem(idx);
    }

    _renderDetail ()
    {
        if (this.props.showDetail === null)
        {
            return (
                <p>Click an item to see its details here.</p>
            );
        }

        let entry = this.props.alphabetical[this.props.showDetail];

        return (
            <Details entry={ entry } />
        );
    }

    render()
    {
        return (
            <Inventory>
                <div className="column is-two-thirds">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Composition</th>
                                <th>Composers (? Uncertain)</th>
                                <th>Folios / Pages</th>
                            </tr>
                        </thead>
                        <tbody>
                        { this.props.alphabetical.map( (entry, idx) =>
                        {
                            return (
                                <tr key={ idx } className="alpha-order" onClick={ () => this.handleShowDetailClick(idx) }>
                                    <td className="item-details">
                                        <h4 className="composition-name">
                                            { entry.composition }
                                        </h4>
                                    </td>
                                    <td>
                                        <Composers composers={ entry.composers } />
                                    </td>
                                    <td>
                                        <Foliation
                                            folio_start={ entry.folio_start }
                                            folio_end={ entry.folio_end }
                                            show_quicklook={ (this.props.user !== null && entry.pages && entry.pages.length > 0) }
                                        />
                                    </td>
                                </tr>
                            )
                        })}
                        </tbody>
                    </table>
                </div>
                <div className="column scroll-sidebar">
                    { this._renderDetail() }
                </div>
            </Inventory>
        );

    }
}

const inventorySelector = state => state.source.inventory;

const alphaSortInventory = createSelector(
    inventorySelector,
    (inventory) => {
        return _.sortBy(inventory, ['composition']);
    }
);

function mapStateToProps (state)
{
    return {
        alphabetical: alphaSortInventory(state),
        showDetail: state.inventory.activeAlphaOrderItem,
        user: state.user
    }
}


export default connect(mapStateToProps, { showAlphaInventoryDetailsForItem })(InventoryAlphabetical);
