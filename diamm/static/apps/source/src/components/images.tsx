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

interface ImagesProps
{
    children?: any;
}


class Images extends React.Component<ImagesProps, void>
{
    render()
    {
        return (
            <TabPanel
                id="source-body-images"
                title="Images"
                route="/images"
            >
                <p>Some images</p>
            </TabPanel>
        );
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Images);
