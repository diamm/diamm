import React from "react";
import { connect } from "react-redux";
import PageCompositionDetails from "./containers/images";

class PageData extends React.Component
{
    render ()
    {
        if (!this.props.pageContents)
            return null;

        return (
            <div className="card is-fullwidth">
                <header className="card-header">
                    <h4 className="card-header-title title is-4 is-not-bold">
                        Folio { this.props.activeCanvasLabel }
                    </h4>
                </header>
                <div className="card-content">
                    <PageCompositionDetails viewer={ this.props.viewer } />
                </div>
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        activeCanvasLabel: state.image_view.activeCanvasLabel,
        pageContents: state.image_view.pageContents
    }
}

export default connect(mapStateToProps)(PageData);
