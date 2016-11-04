import * as React from "react";
import TabPanel from "../containers/tabpanel";
import { connect } from "react-redux";

function mapStateToProps (state: any)
{
    return {};
}

function mapDispatchToProps (dispatch: any)
{
    return {};
}


interface InventoryProps
{
    children?: any;
}

class Inventory extends React.Component<InventoryProps, void>
{
    render()
    {
        return (
            <TabPanel
                id="source-body-inventory"
                title="Inventory"
                route="/inventory"
            >
            </TabPanel>
        );
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Inventory);
