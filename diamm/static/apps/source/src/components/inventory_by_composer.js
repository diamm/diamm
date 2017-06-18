import React from "react";
import {
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
                <div className="column is-two-thirds">
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Composer</th>
                                <th>Compositions</th>
                            </tr>
                        </thead>
                        <tbody>
                        { this.props.inventory.map ((entry, idx) => {
                            return (
                                <tr key={ idx } className="composer-order">
                                    <td className="composer">
                                        <span>{ entry.name }</span>
                                    </td>
                                    <td className="composition-details">
                                        <ul>
                                            { entry.inventory.map ((cmp, idx) => {
                                                return (
                                                    <li key={ idx }>
                                                        { cmp.composition ? cmp.composition : "[No description]" } { cmp.uncertain ? "(?)" : ""}

                                                        <Foliation
                                                            folio_start={ cmp.folio_start }
                                                            folio_end={ cmp.folio_end }
                                                            show_quicklook={ (this.props.user !== null && this.props.source.public_images && entry.pages && entry.pages.length > 0) }
                                                        />
                                                    </li>
                                                );
                                            })}
                                        </ul>
                                    </td>
                                </tr>
                            );
                        }) }
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
        inventory: state.source.composer_inventory,
        user: state.user,
        source: state.source
    }
}

export default connect(mapStateToProps)(InventoryByComposer);
