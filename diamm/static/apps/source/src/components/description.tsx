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

interface DescriptionComponentProps
{
    children?: any;
}

class Description extends React.Component<DescriptionComponentProps, void>
{
    render ()
    {
        return <TabPanel
            id="source-body-description"
            title="Description"
            route="/"
            isDefault={ true }
        >
            <p>a description</p>
        </TabPanel>;
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Description);
