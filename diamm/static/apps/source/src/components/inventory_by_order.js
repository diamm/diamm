import React from "react";
import Inventory from "./inventory";
import { connect } from "react-redux";
import {
    QuickLook,
    Composers,
    Foliation,
} from "./containers/inventory";
import Details from "./inventory_details";
import { showInventoryDetailsForItem } from "../actions/index";


class InventoryByOrder extends React.Component
{
    handleShowDetailClick (idx)
    {
        this.props.showInventoryDetailsForItem(idx);
    }

    render ()
    {
        return (
            <Inventory>
                <div className="source-order-header row">
                    <div className="two columns">
                        Folios / Pages
                    </div>
                    <div className="eight columns">
                        Composition
                    </div>
                    <div className="six columns">
                        Composers (? Uncertain)
                    </div>
                </div>
                { this.props.inventory.map ( (entry, idx) => {
                    const showDetail = this.props.showDetail && this.props.showDetail[idx];
                    const detailClassNames = showDetail ? "fa fa-info-circle fa-border quicklook active" : "fa fa-info-circle fa-border quicklook";

                    return (
                        <div key={ idx } className="source-order row">
                            <div className="two columns">
                                <Foliation
                                    folio_start={ entry.folio_start }
                                    folio_end={ entry.folio_end }
                                    show_quicklook={ (this.props.user !== null && entry.pages && entry.pages.length > 0) }
                                />
                            </div>
                            <div className="eight columns item-details">
                                <h4 className="composition-name">
                                    { entry.composition }
                                    <QuickLook url={ entry.url } />
                                    <i
                                        className={ detailClassNames }
                                        onClick={ () => { this.handleShowDetailClick(idx); }}
                                    />
                                </h4>
                            </div>
                            <div className="six columns">
                                <Composers composers={ entry.composers } />
                            </div>
                            { showDetail &&
                                <Details entry={ entry } /> }
                        </div>
                    );
                })}
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
