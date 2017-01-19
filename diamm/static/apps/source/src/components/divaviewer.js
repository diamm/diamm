import React from "react";
import $ from "jquery";
import diva from "diva.js/build/js/diva.min";
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

        if (this.diva.isInFullscreen())
        {
            b.on('mousemove', function (e)
            {
                let bar = $(".diva-fullscreen-tools");
                bar.fadeIn('medium');
                clearTimeout(t);
                t = setTimeout( function ()
                {
                    bar.fadeOut('medium');
                }, 2000);
            });
        }
        else
        {
            // unsubscribe the mousemove from the toolbar when we exit fullscreen.
            b.off('mousemove');
        }
    }

    getDivaInstance ()
    {
        return $(this.refs.divaContainer).data('diva');
    }

    shouldComponentUpdate ()
    {
        return false;
    }

    // componentWillReceiveProps (nextProps)
    // {
    //     // console.log('component will receive props')
    //     // console.log(nextProps);
    //     let divaInstance = this.getDivaInstance();
    //     divaInstance.gotoPageByLabel(this.nextProps.activeCanvasLabel);
    // }

    componentDidMount ()
    {
        $(this.refs.divaContainer).diva({
            objectData: this.props.manifestURL,
            enableAutoTitle: false,
            fixedHeightGrid: false
        });

        this.diva = $(this.refs.divaContainer).data('diva');

        diva.Events.subscribe("ManifestDidLoad", this.props.onManifestLoaded);
        diva.Events.subscribe("VisiblePageDidChange", this.props.onLoadPageData);
        diva.Events.subscribe("ModeDidSwitch", this.attachFullscreenToolbarHandler.bind(this));
        diva.Events.subscribe("ViewerDidLoad", this.viewerLoaded.bind(this));
    }

    viewerLoaded ()
    {
        if (this.props.activeCanvasLabel)
        {
            this.diva.gotoPageByLabel(this.props.activeCanvasLabel);
        }
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
