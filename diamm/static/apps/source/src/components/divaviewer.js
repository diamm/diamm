import React from "react";
import $ from "jquery";
import diva from "diva.js";
import ReactDOM from "react-dom";
import debounce from "lodash.debounce";


class DivaViewer extends React.Component
{
    constructor (props)
    {
        super(props);
    }

    /*
    *
    * Make the toolbar fade in and out when the mouse is moving.
    * */
    attachFullscreenToolbarHandler ()
    {
        let fullscreenBlock = ReactDOM.findDOMNode(this).getElementsByClassName('diva-fullscreen').item(0);

        let t;
        let b = $(fullscreenBlock);

        b.on('mousemove', function (e)
            {
                let bar = $(".diva-fullscreen-tools");
                bar.fadeIn('medium');
                clearTimeout(t);
                t = setTimeout( function ()
                {
                    bar.fadeOut('medium');
                }, 3000);
            });


    }

    shouldComponentUpdate ()
    {
        return false;
    }

    componentDidMount ()
    {
        $(this.refs.divaContainer).diva({
            objectData: this.props.manifestURL,
            enableAutoTitle: false,
            fixedHeightGrid: false
        });

        diva.Events.subscribe("ManifestDidLoad", this.props.onManifestLoaded);
        diva.Events.subscribe("VisiblePageDidChange", this.props.onLoadPageData);
        diva.Events.subscribe("ModeDidSwitch", this.attachFullscreenToolbarHandler.bind(this));

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
