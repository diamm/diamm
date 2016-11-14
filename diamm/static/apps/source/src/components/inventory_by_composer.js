import React from "react";
import Inventory from "./inventory";
import { connect } from "react-redux";


class InventoryByComposer extends React.Component
{
    render ()
    {
        return (
            <Inventory>
                Composer
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
