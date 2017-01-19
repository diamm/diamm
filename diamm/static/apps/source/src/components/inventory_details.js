import React from "react";
import { connect } from "react-redux";
import {
    Genres,
    Voices,
    Bibliography,
    Attribution,
    Composers,
    ItemNotes
} from "./containers/inventory";

// hardcode the limit at which the sidebar will start scrolling. This is approximately the distance from the top of the
// page.
const __HARDCODED_SCROLL_LIMIT_FOR_GREAT_JUSTICE = 250;

class Details extends React.Component
{
    componentDidMount ()
    {
        window.addEventListener('scroll', this.handleScroll.bind(this));
    }

    componentWillUnmount ()
    {
        window.removeEventListener('scroll', this.handleScroll.bind(this))
    }

    handleScroll (event)
    {
        if (!this.infoCard)
            return;

        if (document.body.scrollTop > __HARDCODED_SCROLL_LIMIT_FOR_GREAT_JUSTICE)
        {
            this.infoCard.classList.add('item-detail-position-fixed');
        }
        else
        {
            // check and re-add class if needed.
            this.infoCard.classList.remove('item-detail-position-fixed');
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
            notes
        } = this.props.entry;

        if (!genres && !voices && !num_voices && !bibliography)
            return null;

        return (
            <div className="item-detail-box" ref={ (card) => { this.infoCard = card; }}>
                <h4 className="title is-4">Item details</h4>

                <div className="card is-fullwidth">
                    <header className="card-header">
                        <h4 className="card-header-title title is-4 is-not-bold">
                            { composition }
                        </h4>
                    </header>
                    <div className="card-content">
                        <Composers composers={ composers } />
                        <Genres genres={ genres }/>
                        <Attribution attribution={ source_attribution } />
                        <Voices voices={ voices } num_voices={ num_voices } />
                        <ItemNotes notes={ notes } />
                        <Bibliography entry={ bibliography } />
                    </div>
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
    }
}

export default connect(mapStateToProps)(Details);

