import React from "react";
import Inventory from "./inventory";
import { connect } from "react-redux";
import {
    QuickLook,
    Composers,
    Foliation,
} from "./containers/inventory";
import Details from "./inventory_details";
import InventoryUninventoried from "./inventory_uninventoried";
import { showInventoryDetailsForItem } from "../actions/index";


class InventoryByOrder extends React.Component
{
    handleShowDetailClick (idx)
    {
        this.props.showInventoryDetailsForItem(idx);
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
                        const showDetail = this.props.showDetail && this.props.showDetail[idx];
                        const detailClassNames = showDetail ? "fa fa-chevron-circle-up fa-border quicklook active" : "fa fa-chevron-circle-down fa-border quicklook";

                        return (
                            <tr key={ idx }>
                                <td>
                                    <Foliation
                                        folio_start={ entry.folio_start }
                                        folio_end={ entry.folio_end }
                                        show_quicklook={ (this.props.user !== null && entry.pages && entry.pages.length > 0) }
                                    />
                                </td>
                                <td className="item-details">
                                    <h4 className="composition-name">
                                        { entry.composition }
                                        <QuickLook url={ entry.url } />
                                        <i
                                            className={ detailClassNames }
                                            onClick={ () => { this.handleShowDetailClick(idx); }}
                                        />
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
        showDetail: state.tabs.showInventoryDetail
    }
}

export default connect(mapStateToProps, { showInventoryDetailsForItem })(InventoryByOrder);
