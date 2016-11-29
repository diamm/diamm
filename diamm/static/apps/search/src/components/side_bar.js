import React from "react";
import { connect } from "react-redux";


class SideBar extends React.Component
{
    render ()
    {
        return (
            <div>
                Sidebar.
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {};
}

export default connect(mapStateToProps)(SideBar);
