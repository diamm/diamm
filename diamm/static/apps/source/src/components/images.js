import React from "react";
import { connect } from "react-redux";
import debounce from "lodash.debounce";
import _ from "lodash";

import DivaViewer from "./divaviewer";
import PageData from "./page_data";
import { ControlBar } from "./containers/images";
import {
    setActiveManifest,
    setCurrentlyActiveCanvas,
    setCurrentlyActiveCanvasTitle,
    fetchActiveRanges,
    clearPageContents
} from "../actions/iiif_actions";



class Images extends React.Component
{
    /*
    * Called when a page switches in the viewer.
    * */
    loadPageData = debounce( (pageIndex, pageName) =>
    {
        this.props.clearPageContents();

        let canvas = this.props.manifest.sequences[0].canvases[pageIndex]["@id"];
        let canvasTitle = this.props.manifest.sequences[0].canvases[pageIndex]["label"];
        let ranges = this.props.rangeLookup[canvas];

        this.props.setCurrentlyActiveCanvas(canvas);
        this.props.setCurrentlyActiveCanvasTitle(canvasTitle);

        if (ranges)
        {
            this.props.fetchActiveRanges(ranges);
        }

    }, 50);

    /*
    * Called when the IIIF Manifest has been loaded and is available.
    * Also dispatches a function to compute the page and canvas ranges.
    * */
    manifestLoaded (manifest)
    {
        this.props.setActiveManifest(manifest);
    }

    componentDidMount ()
    {
        /*
         * Once the viewer has loaded, check the URL for any
         * query params that have been passed along, as this is how
         * we'll scroll Diva to the right page, based on the image filename URL.
         * */
        let hashparams = window.location.hash;
        let qparams = _.last(hashparams.split("?"));

        if (qparams)
        {
            let params = new URLSearchParams(qparams);
            if (!params.has('p'))
                return;

            this.props.setCurrentlyActiveCanvasTitle(params.get('p'));
        }
    }

    render()
    {
        return (
            <div className="columns">
                <div className="column is-three-quarters">
                    <DivaViewer
                        ref="divaViewer"
                        manifestURL={ this.props.manifestURL }
                        onLoadPageData={ this.loadPageData.bind(this) }
                        onManifestLoaded={ this.manifestLoaded.bind(this) }
                        activeCanvasLabel={ this.props.activeCanvasLabel }
                    />
                </div>
                <div className="column">
                    <PageData />
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        manifestURL: state.source.manifest_url,
        manifest: state.manifest,
        rangeLookup: state.image_view.ranges,
        activeCanvasLabel: state.image_view.activeCanvasLabel

    }
}

const mapDispatchToProps = {
    setActiveManifest,
    setCurrentlyActiveCanvas,
    setCurrentlyActiveCanvasTitle,
    fetchActiveRanges,
    clearPageContents
};

export default connect(mapStateToProps, mapDispatchToProps)(Images);
