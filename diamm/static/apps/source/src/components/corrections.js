import React from "react"
import { connect } from "react-redux";


class Correction extends React.Component
{
    render ()
    {
        return (
            <div>Hello world</div>
        );
    }
}

function mapStateToProps ()
{
    return {};
}

export default connect(mapStateToProps)(Correction);
