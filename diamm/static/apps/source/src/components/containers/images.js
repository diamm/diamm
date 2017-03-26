import React from "react";
import { connect } from "react-redux";
import { Link } from "react-router";
import {
    Composers,
    Genres
} from "./inventory";
import {
    IMAGES_ROUTE
} from "../../routes";


class PageCompositionDetails extends React.Component
{
    gotoPageInViewer (label)
    {
        this.props.viewer.diva.gotoPageByLabel(label);
    }

    _pages (pages)
    {
        return (
            <div>
                <strong>Appears on: </strong>

                { pages.map( (page, idx) =>
                {
                    return <span key={ idx }><a onClick={ () => this.gotoPageInViewer(page.label) }>{ page.label }</a> </span>
                })}
            </div>);
    }

    render ()
    {
        if (!this.props.pageContents)
            return null;

        return (
            <div className="image-composition-details">
                { this.props.pageContents.map( (entry, idx) => {
                    return (<div key={ idx }>
                        <h5 className="title is-5 is-marginless">
                            <a href={ entry.composition["@id"]}>
                                { entry.composition.title }
                            </a>
                        </h5>
                        <Genres genres={ entry.composition.genres } />
                        <Composers composers={ entry.composers } />
                        { this._pages(entry.pages) }
                    </div>);
                })}
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        pageContents: state.image_view.pageContents
    }
}

export default connect(mapStateToProps)(PageCompositionDetails);
