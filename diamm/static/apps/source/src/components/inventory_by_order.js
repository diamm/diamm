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

    _renderDetail ()
    {
        if (this.props.showDetail === null)
        {
            return (
                <p>Click an item to see its details here.</p>
            );
        }

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
                <div className="column is-two-thirds">
                    <table className="table">
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
                            return (
                                <tr key={ idx }
                                    onClick={ () => this.handleShowDetailClick(idx) }
                                    className={ idx === this.props.showDetail ? "selected" : ""}
                                >
                                    <td>
                                        <Foliation
                                            folio_start={ entry.folio_start }
                                            folio_end={ entry.folio_end }
                                            show_quicklook={ (this.props.user !== null && entry.pages && entry.pages.length > 0) }
                                        />
                                    </td>
                                    <td className="item-details">
                                        <h4 className="composition-name">
                                            { `${entry.composition} ` }
                                        </h4>
                                    </td>
                                    <td>
                                        <Composers composers={ entry.composers } />
                                    </td>
                                </tr>
                            );
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

function mapStateToProps (state)
{
    return {
        inventory: state.source.inventory,
        public_images: state.source.public_images,
        has_images: state.source.has_images,
        user: state.user,
        showDetail: state.inventory.activeSourceOrderItem
    }
}

export default connect(mapStateToProps, { showInventoryDetailsForItem })(InventoryByOrder);
