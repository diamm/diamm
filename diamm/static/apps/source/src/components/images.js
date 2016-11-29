import React from "react";
import { connect } from "react-redux";
import debounce from "lodash.debounce";

import DivaViewer from "./divaviewer";
import PageData from "./page_data";
import { ControlBar } from "./containers/images";
import {
    setActiveManifest,
    setCurrentlyActiveCanvas,
    setCurrentlyActiveCanvasTitle
} from "../actions/iiif_actions";



class Images extends React.Component
{
    /*
    * Called when a page switches in the viewer.
    * */
    loadPageData = debounce( (pageIndex, pageName) =>
    {
        let canvas = this.props.manifest.sequences[0].canvases[pageIndex]["@id"];
        let canvasTitle = this.props.manifest.sequences[0].canvases[pageIndex]["label"];
        let ranges = this.props.rangeLookup[canvas];

        this.props.setCurrentlyActiveCanvas(canvas);
        this.props.setCurrentlyActiveCanvasTitle(canvasTitle);
    });

    /*
    * Called when the IIIF Manifest has been loaded and is available
    * */
    manifestLoaded (manifest)
    {
        this.props.setActiveManifest(manifest);
    }

    render()
    {
        return (
            <div className="row">
                <div className="six columns">
                    <PageData />
                </div>
                <div className="ten columns">
                    <DivaViewer
                        ref="divaViewer"
                        manifestURL={ this.props.manifestURL }
                        onLoadPageData={ this.loadPageData.bind(this) }
                        onManifestLoaded={ this.manifestLoaded.bind(this) }
                    />
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        manifestURL: state.source.iiif_manifest,
        manifest: state.manifest,
        rangeLookup: state.image_view.ranges

    }
}

const mapDispatchToProps = {
    setActiveManifest,
    setCurrentlyActiveCanvas,
    setCurrentlyActiveCanvasTitle
};

export default connect(mapStateToProps, mapDispatchToProps)(Images);
