import React from "react";
import { connect } from "react-redux";
import {
    Genres,
    Voices,
    Bibliography,
    Attribution,
    Composers,
    ItemNotes,
    Foliation
} from "./containers/inventory";

// hardcode the limit at which the sidebar will start scrolling. This is approximately the distance from the top of the
// page. Slightly silly name so that it doesn't get mistaken for a publicly usable constant.
const __HARDCODED_SCROLL_LIMIT_FOR_GREAT_JUSTICE = 250;

class Details extends React.Component
{
    // componentDidMount ()
    // {
    //     window.addEventListener('scroll', this.handleScroll.bind(this));
    // }

    // componentWillUnmount ()
    // {
    //     window.removeEventListener('scroll', this.handleScroll.bind(this))
    // }
    //
    // handleScroll (event)
    // {
    //     if (!this.infoCard)
    //         return;
    //
    //     if (document.body.scrollTop > __HARDCODED_SCROLL_LIMIT_FOR_GREAT_JUSTICE)
    //     {
    //         this.infoCard.classList.add('item-detail-position-fixed');
    //     }
    //     else
    //     {
    //         // check and re-add class if needed.
    //         this.infoCard.classList.remove('item-detail-position-fixed');
    //     }
    // }

    _renderEdit (pk)
    {
        if (this.props.user && this.props.user.isStaff)
        {
            let editUrl = `/admin/diamm_data/item/${pk}`;
            return (
                <div className="columns">
                    <div className="column">
                        <a className="button" href={ editUrl }>
                            Edit
                        </a>
                    </div>
                </div>
            )
        }
    }

    render ()
    {
        const {
            genres,
            voices,
            num_voices,
            bibliography,
            source_attribution,
            composition,
            composers,
            notes,
            url,
            folio_start,
            folio_end,
            pages,
            pk
        } = this.props.entry;

        if (!genres && !voices && !num_voices && !bibliography)
            return null;

        return (
            <td colSpan="3">
                <div className="columns">
                    <header className="column">
                        <h4 className="title is-4">
                            <a href={ url }>{ composition }</a>
                        </h4>
                        <h5 className="subtitle is-5">
                            <Composers composers={ composers } />
                        </h5>
                    </header>
                </div>
                <div className="columns">
                    <div className="column">
                        <div>
                            <strong>Appears on: </strong>
                            <Foliation
                                folio_start={ folio_start }
                                folio_end={ folio_end }
                                show_quicklook={ (this.props.user.is_authenticated !== false && this.props.source.public_images && pages && pages.length > 0) }
                            />
                        </div>
                        <Genres genres={ genres }/>
                        <Attribution attribution={ source_attribution } />
                        <Voices voices={ voices } num_voices={ num_voices } />
                    </div>
                    <div className="column">
                        <ItemNotes notes={ notes } />
                        <Bibliography entry={ bibliography } />
                    </div>
                </div>
                { this._renderEdit(pk) }
            </td>
        );
    }
}

function mapStateToProps (state)
{
    return {
        user: state.user,
        source: state.source
    }
}

export default connect(mapStateToProps)(Details);

