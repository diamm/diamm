import React from "react";
import { connect } from "react-redux";
import {
    Composers,
    Foliation,
    Voices
} from "./containers/inventory";

/*
* Some sources contain an 'inventory' that say 'this source has not been inventoried,
* but here are the composers and the number of works we know are in it.
* */
class InventoryUninventoried extends React.Component
{
    render ()
    {
        return (
            <div className="columns">
                <div className="column">
                    <p>This source has not been inventoried. However, it is known to contain:</p>
                    <table className="table inventory-table">
                        <tbody>
                        { this.props.uninventoried.map( (entry, idx) => {
                            return (
                                <tr key={ idx }>
                                    <td>
                                        <Foliation
                                            folio_start={ entry.folio_start }
                                            folio_end={ entry.folio_end }
                                            show_quicklook={ (this.props.user.is_authenticated !== false && this.props.source.public_images && entry.pages && entry.pages.length > 0) }
                                        />
                                    </td>
                                    <td className="item-details">
                                        { entry.source_attribution || "[No Source Attribution]" }
                                    </td>
                                    <td>
                                        <Composers
                                          composers={ entry.composers }
                                        />
                                    </td>
                                    { entry.voices && <td><Voices voices={ entry.voices } num_voices={ entry.voices.length } /></td> }
                                </tr>
                            );
                        })}
                        </tbody>
                    </table>
                    <hr />
                    <p>
                        If you would like to contribute an inventory please get in touch. E-mail
                        <a href="mailto:diamm@music.ox.ac.uk">diamm@music.ox.ac.uk</a>.
                    </p>
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        uninventoried: state.source.uninventoried,
        user: state.user,
        source: state.source
    }
}

export default connect(mapStateToProps)(InventoryUninventoried);
