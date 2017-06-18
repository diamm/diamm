import React from "react";
import Inventory from "./inventory";
import { connect } from "react-redux";
import {
    Composers,
    Foliation,
} from "./containers/inventory";
import Details from "./inventory_details";
import InventoryUninventoried from "./inventory_uninventoried";
import { showInventoryDetailsForItem } from "../actions/inventory";


class InventoryByOrder extends React.Component
{
    handleShowDetailClick (idx)
    {
        this.props.showInventoryDetailsForItem(idx);
    }

    _renderDetail (idx)
    {
        if (this.props.showDetail !== idx)
            return null;

        let entry = this.props.inventory[this.props.showDetail];
        return (
            <Details entry={ entry } />
        );
    }

    render ()
    {
        if (this.props.inventory.length === 0)
            return (
                <Inventory>
                    <InventoryUninventoried />
                </Inventory>
            );
        return (
            <Inventory>
                <div className="column">
                    <p>Click an entry to see more information about that item.</p>
                    <table className="table inventory-table">
                        <thead>
                            <tr>
                                <th>
                                    Folios / Pages
                                </th>
                                <th>
                                    Composition
                                </th>
                                <th>
                                    Composers (? Uncertain)
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                        { this.props.inventory.map ( (entry, idx) => {

                            if (this.props.showDetail === idx)
                            {
                                return (
                                    <tr key={ idx } className="selected">
                                        { this._renderDetail(idx) }
                                    </tr>
                                )
                            }
                            else
                            {
                                return (
                                    <tr key={ idx }
                                        onClick={ () => this.handleShowDetailClick(idx) }
                                    >
                                        <td>
                                            <Foliation
                                                folio_start={ entry.folio_start }
                                                folio_end={ entry.folio_end }
                                                show_quicklook={ (this.props.user !== null && this.props.source.public_images && entry.pages && entry.pages.length > 0) }
                                            />
                                        </td>
                                        <td className="item-details">
                                            { `${entry.composition} ` }
                                        </td>
                                        <td>
                                            <Composers composers={ entry.composers } />
                                        </td>
                                    </tr>
                                );
                            }
                        })}
                        </tbody>
                    </table>
                </div>
            </Inventory>
        );
    }
}

function mapStateToProps (state)
{
    return {
        inventory: state.source.inventory,
        public_images: state.source.public_images,
        has_images: state.source.has_images,
        user: state.user,
        showDetail: state.inventory.activeSourceOrderItem,
        source: state.source
    }
}

export default connect(mapStateToProps, { showInventoryDetailsForItem })(InventoryByOrder);
