import React from "react";
import { connect } from "react-redux";


class Contributors extends React.Component
{
    render ()
    {
        return (
            <div>
                Credits
            </div>
        );
    }
}

export default connect()(Contributors);
