import React from "react";
import { connect } from "react-redux";
import {
    Composers,
    Genres
} from "./inventory";


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
                    let sourceAttribution, genres, composers;

                    if (entry.hasOwnProperty('source_attribution'))
                        sourceAttribution  = entry.source_attribution;

                    if (entry.hasOwnProperty('composition') && entry.composition.hasOwnProperty('genres'))
                        genres = entry.composition.genres;

                    if (entry.hasOwnProperty('composers'))
                        composers = entry.composers;

                    return (<div key={ idx }>
                        <h5 className="title is-5 is-marginless">
                            <ItemTitleLink entry={ entry } />
                        </h5>
                        <Attribution attribution={ sourceAttribution } />
                        <Genres genres={ genres } />
                        <Composers composers={ composers } />
                        { this._pages(entry.pages) }
                    </div>);
                })}
            </div>
        );
    }
}


const ItemTitleLink = ({entry}) => {
    if (entry.hasOwnProperty('composition') && entry.composition.hasOwnProperty('title'))
    {
        return (<a href={ entry.composition['@id'] }>
            { entry.composition.title }
        </a>);
    }
    else if (entry.hasOwnProperty('item_title'))
    {
        return (
            <span>{ entry.item_title }</span>
        );
    }
    else
    {
        return (
            <span>[No title]</span>
        );
    }
};

function mapStateToProps (state)
{
    return {
        pageContents: state.image_view.pageContents
    }
}

export default connect(mapStateToProps)(PageCompositionDetails);
