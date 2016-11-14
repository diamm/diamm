import React from "react";
import { connect } from "react-redux";
import { InventoryMenu } from "./containers/inventory";

class Inventory extends React.Component
{
    render ()
    {
        return (
            <div className="row">
                <div className="sixteen columns source-inventory">
                    <InventoryMenu />
                    { this.props.children }
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {}
}

export default connect(mapStateToProps)(Inventory);
