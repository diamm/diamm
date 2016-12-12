import React from "react";
import classNames from "classnames";

export default class Facet extends React.Component
{
    static propTypes = {
        title: React.PropTypes.string.isRequired,
        controls: React.PropTypes.node,
        bodyClasses: React.PropTypes.string
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
                    <h4>{ this.props.title }</h4>
                    { this.props.controls }
                </div>
                <div className={ bodyClasses }>
                    { this.props.children }
                </div>
            </div>
        )
    }
}
