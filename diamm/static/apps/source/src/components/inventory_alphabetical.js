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
import { showAlphaInventoryDetailsForItem } from "../actions/index";

class InventoryAlphabetical extends React.Component
{
    handleShowDetailClick (idx)
    {
        this.props.showAlphaInventoryDetailsForItem(idx);
    }

    render()
    {
        return (
            <Inventory>
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
                        const showDetail = this.props.showDetail && this.props.showDetail[idx];
                        const detailClassNames = showDetail ? "fa fa-chevron-circle-up fa-border quicklook active" : "fa fa-chevron-circle-down fa-border quicklook";

                        return (
                            <tr key={ idx } className="alpha-order">
                                <td className="item-details">
                                    <h4 className="composition-name">
                                        { entry.composition }
                                        <QuickLook url={ entry.url } />
                                        <i className={ detailClassNames } onClick={ () => this.handleShowDetailClick(idx) } />
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
        user: state.user
    }
}


export default connect(mapStateToProps, { showAlphaInventoryDetailsForItem })(InventoryAlphabetical);
