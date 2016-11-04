import * as React from "react";
import { connect } from "react-redux";
import TabPanel from "../containers/tabpanel";

function mapStateToProps (state: any)
{
    console.log(state);
    return {};
}

function mapDispatchToProps (dispatch: any)
{
    console.log(dispatch);
    return {};
}


interface BibliographyProps
{
    foo?: string;
    onFoo?: any;
    children?: any;
}

class Bibliography extends React.Component<BibliographyProps, void>
{
    render()
    {
        console.log(this.props);
        return <TabPanel
            id="source-body-bibliography"
            title="Bibliography"
            route="/bibliography">
        </TabPanel>;
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Bibliography);
