import * as React from "react";
import { connect } from "react-redux";
import TabContainer from "../containers/tabcontainer";
import Description from "./description";
import Inventory from "./inventory";
import Images from "./images";
import Sets from "./sets";
import Bibliography from "./bibliography";

function mapStateToProps (state: any)
{
    return {};
}

function mapDispatchToProps (dispatch: any)
{
    return {};
}


interface SourceComponentProps
{
    children?: any;
}

class Source extends React.Component<SourceComponentProps, void>
{
    render()
    {
        return (
            <TabContainer>
                <Description />
                <Images />
                <Inventory />
                <Sets />
                <Bibliography />
            </TabContainer>
        );
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Source);
