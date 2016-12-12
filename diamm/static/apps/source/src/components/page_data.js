import React from "react";
import { connect } from "react-redux";

class PageData extends React.Component
{
    render ()
    {
        return (
            <div>
                Folio { this.props.activeCanvasLabel }
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        activeCanvasLabel: state.image_view.activeCanvasLabel
    }
}

export default connect(mapStateToProps)(PageData);
