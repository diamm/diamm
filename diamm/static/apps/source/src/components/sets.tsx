import * as React from "react";
import { connect } from "react-redux";
import TabPanel from "../containers/tabpanel";

function mapStateToProps (state: any)
{
    return {};
}

function mapDispatchToProps (dispatch: any)
{
    return {};
}


interface SetsProps
{
    children?: any;
}

class Sets extends React.Component<SetsProps, void>
{
    render()
    {
        return (
            <TabPanel
                id="source-body-sets"
                title="Sets"
                route="/sets"
            >
            </TabPanel>
        );
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Sets);
