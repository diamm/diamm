import React from "react";
import $ from "jquery";


class DivaViewer extends React.Component
{
    shouldComponentUpdate ()
    {
        return false;
    }

    componentDidMount ()
    {
        this.diva = $(this.refs.divaviewer).diva({
            objectData: "https://alpha.diamm.ac.uk/sources/117/manifest/"
        });
    }

    render ()
    {
        return (
            <div id="diva-viewer" ref="divaviewer"/>
        );
    }
}

export default DivaViewer;
