import React from "react";
import { connect } from "react-redux";

class PageData extends React.Component
{
    render ()
    {
        return (
            <div>
                Folio { this.props.activeCanvasTitle }
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        activeCanvasTitle: state.image_view.activeCanvasTitle
    }
}

export default connect(mapStateToProps)(PageData);
