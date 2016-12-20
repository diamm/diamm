import React from "react";
import { connect } from "react-redux";


class Source extends React.Component
{
    render ()
    {
        return (
            <div>Source.</div>
        );
    }
}

export default connect()(Source);
