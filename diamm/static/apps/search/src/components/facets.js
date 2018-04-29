import React from "react";
import classNames from "classnames";
import PropTypes from "prop-types";

export default class Facet extends React.Component
{
    static propTypes = {
        title: PropTypes.string.isRequired,
        controls: PropTypes.node,
        bodyClasses: PropTypes.string
    };

    render ()
    {
        // let bc = this.props.bodyClasses;

        let bodyClasses = classNames(
            "facet-body",
            this.props.bodyClasses
        );
        return (
            <div className="facet-block">
                <div className="facet-title">
                    { this.props.title }
                    { this.props.controls }
                </div>
                <div className={ bodyClasses }>
                    { this.props.children }
                </div>
            </div>
        )
    }
}
