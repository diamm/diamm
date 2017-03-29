import React from "react";
import { connect } from "react-redux";
import { InventoryMenu } from "./containers/inventory";
import QuickLook from "./quicklook";

class Inventory extends React.Component
{
    render ()
    {
        return (
            <div>
                <div className="columns">
                    {/* Only mount this component if the type is set on quicklook.
                     This lets the QuickLook component's lifecycle method control
                     the overflow styles for body, since the component will
                     unmount when the quicklook prop is empty. */}
                    { this.props.quicklook.type &&
                    <QuickLook content={ this.props.quicklook }/> }

                    <div className="column">
                        <nav className="level">
                            <div className="level-left">
                                <div className="level-item">
                                    <InventoryMenu
                                        source_order={ this.props.source_order }
                                        composer_order={ this.props.composer_order }
                                        uninventoried={ this.props.uninventoried }
                                    />
                                </div>
                            </div>
                        </nav>
                    </div>
                </div>
                <div className="columns">
                    { this.props.children }
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        source_order: state.source.inventory,
        composer_order: state.source.composer_inventory,
        uninventoried: state.source.uninventoried,
        quicklook: state.quicklook
    }
}

export default connect(mapStateToProps)(Inventory);
