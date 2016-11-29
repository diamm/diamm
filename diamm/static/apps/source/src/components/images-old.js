import React from "react";
import DivaViewer from "./divaviewer";
import { connect } from "react-redux";
import debounce from "lodash.debounce";
import _ from "lodash";
import {
    iiifManifestDidLoad,
    fetchActiveRanges,
    setCurrentlyActiveCanvas,
    setCurrentlyActiveCanvasTitle
} from "../actions/iiif_actions";
import { ControlBar } from "./containers/images";

const DEBOUNCE_INTERVAL = 300;


class Images extends React.Component
{
    constructor (props)
    {
        super(props);
        this.state = { 'structures': null };
    }

    _loadPageData = debounce( (pageIndex, pageName) =>
    {
        let canvas = this.props.manifest.sequences[0].canvases[pageIndex]['@id'];
        let canvasTitle = this.props.manifest.sequences[0].canvases[pageIndex]['label'];
        let ranges = this.state.structures[canvas];

        this.props.setCurrentlyActiveCanvas(canvas);
        this.props.setCurrentlyActiveCanvasTitle(canvasTitle);

        console.log('ranges: ', ranges);
        console.log('activeRanges: ', this.props.activeRanges);

        if (ranges && !(_.isEqual(ranges, this.props.activeRanges)))
        {
            this.props.fetchActiveRanges(ranges);
        }

    }, DEBOUNCE_INTERVAL);

    /*
     *  Precomputes a lookup for canvas => ranges so that we can
     *  fetch data for all ranges that are currently being shown.
    **/
    _manifestLoaded (manifest)
    {
        this.props.iiifManifestDidLoad(manifest);

        let rangelookup = (structures) => {
            let out = {};
            structures.map( (entry) =>{
                let range = entry["@id"];
                entry.members.map( (member) =>{
                    let canvas = member["@id"];
                    _.has(out, canvas) ? _.concat(out[canvas], [range]) : out[canvas] = [range];
                })
            });
            return out;
        };

        this.setState({'structures': rangelookup(manifest.structures)});
    };

    render ()
    {
        return (
            <div className="row">
                <div className="six columns">
                    <button onClick={ () => this.refs.divaViewer.foo() }>Grid</button>
                </div>
                <div className="ten columns">
                    <ControlBar />
                    <DivaViewer
                        manifest={ this.props.manifest_url }
                        loadPageData={ this._loadPageData.bind(this) }
                        manifestLoaded={ this._manifestLoaded.bind(this) }
                        ref="divaViewer"
                    />
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        manifest_url: state.source.iiif_manifest,
        manifest: state.manifest,
        activeRanges: state.image_view.activeRanges,
        activeCanvas: state.image_view.activeCanvas
    }
}

const mapDispatchToProps = {
    iiifManifestDidLoad,
    fetchActiveRanges,
    setCurrentlyActiveCanvas,
    setCurrentlyActiveCanvasTitle
};

export default connect(mapStateToProps, mapDispatchToProps)(Images);
