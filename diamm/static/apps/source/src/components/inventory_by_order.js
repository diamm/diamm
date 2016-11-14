import React from "react";
import Inventory from "./inventory";
import { connect } from "react-redux";
import {
    QuickLook,
    Composers,
    Foliation,
    Details
} from "./containers/inventory";

class InventoryByOrder extends React.Component
{
    render ()
    {
        // console.log(this.props.inventory);

        return (
            <Inventory>
                { this.props.inventory.map ( (entry, idx) => {
                    return (
                        <div key={ idx } >
                            <table className="source-order">
                                <tbody>
                                    <tr>
                                        <td className="foliation">
                                            <Foliation
                                                folio_start={ entry.folio_start }
                                                folio_end={ entry.folio_end }
                                                show_quicklook={ this.props.authenticated !== false && this.props.has_images !== false && this.props.public_images !== false }
                                            />
                                        </td>
                                        <td className="composition-info">
                                            <h4 className="composition-name">
                                                { entry.composition }
                                                <QuickLook url={ entry.url } />
                                            </h4>
                                        </td>
                                        <td className="composers">
                                            <Composers composers={ entry.composers } />
                                        </td>
                                    </tr>
                                    <Details
                                        genres={ entry.genres }
                                        voices={ entry.voices }
                                        num_voices={ entry.num_voices }
                                        bibliography={ entry.bibliography }
                                    />
                                </tbody>
                            </table>
                            <hr />
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
        authenticated: state.user.isAuthenticated
    }
}

export default connect(mapStateToProps)(InventoryByOrder);
