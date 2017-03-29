import React from "react";
import { connect } from "react-redux";
import { Composers } from "./containers/inventory";

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
                    <p>This source has not been inventoried. It is known to contain
                        works by:</p>
                    { this.props.uninventoried.map( (itm, idx) => {
                        return (
                            <div key={ idx }>
                                <Composers
                                  composers={ itm.composers }
                                />
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        uninventoried: state.source.uninventoried
    }
}

export default connect(mapStateToProps)(InventoryUninventoried);
