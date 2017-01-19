import React from "react";
import { connect } from "react-redux";

class PageData extends React.Component
{
    render ()
    {
        return (
            <div>
                Folio { this.props.activeCanvasLabel }

                { this.props.pageContents.map( (itm, idx) =>
                {
                    if (itm.composition)
                    {
                        return <p key={ idx }>{ itm.composition.title }</p>
                    }
                })}
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
