import React from "react";
import {
    QuickLook,
    Foliation
} from "./containers/inventory";
import Inventory from "./inventory";
import { connect } from "react-redux";


class InventoryByComposer extends React.Component
{
    render ()
    {
        return (
            <Inventory>
                <div className="row composer-order-header">
                    <div className="three columns">
                        <span>Composer</span>
                    </div>
                    <div className="thirteen columns">
                        <span>Compositions</span>
                    </div>
                </div>
                { this.props.inventory.map ((entry, idx) => {
                    return (
                        <div key={ idx } className="composer-order row">
                            <div className="three columns composer">
                                <span>{ entry.name }</span>
                                <QuickLook url={ entry.url } />
                            </div>
                            <div className="thirteen columns composition-details">
                                <ul>
                                { entry.inventory.map ((cmp, idx) => {
                                    return (
                                        <li key={ idx }>
                                            { cmp.composition } { cmp.uncertain ? "(?)" : ""}
                                            <QuickLook url={ cmp.url } />
                                            <Foliation
                                                folio_start={ cmp.folio_start }
                                                folio_end={ cmp.folio_end }
                                                show_quicklook={ (this.props.authenticated !== false && entry.pages && entry.pages.length > 0) }
                                            />
                                        </li>
                                    );
                                })}
                                </ul>
                            </div>
                        </div>
                    );
                }) }
            </Inventory>
        );
    }
}

function mapStateToProps (state)
{
    return {
        inventory: state.source.composer_inventory
    }
}

export default connect(mapStateToProps)(InventoryByComposer);
