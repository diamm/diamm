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
                <div className="alpha-order-header row">
                    <div className="eight columns">
                        Composition
                    </div>
                    <div className="six columns">
                        Composers (? Uncertain)
                    </div>
                    <div className="two columns">
                        Folios / Pages
                    </div>
                </div>
                { this.props.alphabetical.map( (entry, idx) =>
                {
                    const showDetail = this.props.showDetail && this.props.showDetail[idx];
                    const detailClassNames = showDetail ? "fa fa-info-circle fa-border quicklook active" : "fa fa-info-circle fa-border quicklook";

                    return (
                        <div key={ idx } className="alpha-order row">
                            <div className="eight columns item-details">
                                <h4 className="composition-name">
                                    { entry.composition }
                                    <QuickLook url={ entry.url } />
                                    <i className={ detailClassNames } onClick={ () => this.handleShowDetailClick(idx) } />
                                </h4>
                            </div>
                            <div className="six columns">
                                <Composers composers={ entry.composers } />
                            </div>
                            <div className="two columns">
                                <Foliation
                                    folio_start={ entry.folio_start }
                                    folio_end={ entry.folio_end }
                                    show_quicklook={ (this.props.user !== null && entry.pages && entry.pages.length > 0) }
                                />
                            </div>
                            { showDetail &&
                                <Details entry={ entry } /> }
                        </div>
                    )
                })}
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
