import React from "react";
import Inventory from "./inventory";
import { connect } from "react-redux";
import _ from "lodash";
import { createSelector } from "reselect";
import { withRouter } from "react-router-dom";

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

    _renderDetail (idx)
    {
        if (this.props.showDetail !== idx)
            return null;

        let entry = this.props.alphabetical[this.props.showDetail];

        return (
            <Details entry={ entry } />
        );
    }

    render()
    {
        console.log('alphabetical inventory render!');

        return (
            <Inventory>
                <div className="column">
                    <p>Click an entry to see more information about that item.</p>
                    <table className="table inventory-table">
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
                            if (this.props.showDetail === idx)
                            {
                                return (
                                    <tr key={ idx }>
                                        { this._renderDetail(idx) }
                                    </tr>
                                )
                            }
                            return (
                                <tr key={ idx } className="alpha-order" onClick={ () => this.handleShowDetailClick(idx) }>
                                    <td className="item-details">
                                        { entry.composition }
                                    </td>
                                    <td>
                                        <Composers composers={ entry.composers } />
                                    </td>
                                    <td>
                                        <Foliation
                                            folio_start={ entry.folio_start }
                                            folio_end={ entry.folio_end }
                                            show_quicklook={ (this.props.user.is_authenticated !== false && this.props.source.public_images && entry.pages && entry.pages.length > 0) }
                                        />
                                    </td>
                                </tr>
                            )
                        })}
                        </tbody>
                    </table>
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
        user: state.user,
        source: state.source
    }
}


export default withRouter(connect(mapStateToProps, { showAlphaInventoryDetailsForItem })(InventoryAlphabetical));
