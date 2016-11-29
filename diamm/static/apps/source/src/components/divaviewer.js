import React from "react";
import $ from "jquery";
import diva from "diva.js";


class DivaViewer extends React.Component
{
    constructor (props)
    {
        super(props);
    }

    shouldComponentUpdate ()
    {
        return false;
    }

    componentDidMount ()
    {
        console.log(this.props.manifestURL);

        $(this.refs.divaContainer).diva({
            objectData: this.props.manifestURL,
            enableAutoTitle: false,
            fixedHeightGrid: false
        });

        diva.Events.subscribe("ManifestDidLoad", this.props.onManifestLoaded);
        diva.Events.subscribe("VisiblePageDidChange", this.props.onLoadPageData);

        this.diva = $(this.refs.divaContainer).data('diva');
    }

    render ()
    {
        if (!this.props.manifestURL)
            return null;

        return (
            <div id="divaContainer" ref="divaContainer"/>
        );
    }
}

export default DivaViewer;
