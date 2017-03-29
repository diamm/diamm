import React from "react";
import { connect } from "react-redux";


class Person extends React.Component
{
    render ()
    {
        return (
            <div>Person.</div>
        );
    }
}

export default connect()(Person)
