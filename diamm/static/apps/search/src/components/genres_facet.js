import React from "react"
import _ from "lodash";
import { connect } from "react-redux";
import Facet from "./facets";
// import {
//     toggleFacetShowAll
// } from "../actions/facets";
import {
    FACET_UPDATE_GENRE_TOGGLE
} from "../constants";
import {
    addGenreToActive,
    removeGenreFromActive,
    clearActiveGenres,
    performGenreSearch
} from "../actions/genre_facet";


class GenresFacet extends React.Component
{
    toggleGenre (value)
    {
        if (this.props.active.includes(value))
            this.deselectGenre(value);
        else
            this.selectGenre(value);
    }

    selectGenre (value)
    {
        this.props.addGenreToActive(value);
        this.props.performGenreSearch();
    }

    deselectGenre (value)
    {
        this.props.removeGenreFromActive(value);
        this.props.performGenreSearch();
    }

    clearActiveGenres ()
    {
        this.props.clearActiveGenres();
        this.props.performGenreSearch();
    }

    // toggleShowAll (toggle)
    // {
    //     this.props.toggleFacetShowAll(!toggle, FACET_UPDATE_GENRE_TOGGLE)
    // }

    _showControls ()
    {
        return (
            <div
                className="facet-show-control"
                onClick={ () => this.clearActiveGenres() }
            >
                Clear all
            </div>
        )
    }

    render ()
    {
        let facets = _.chunk(this.props.genres, 2);

        return (
            <Facet
                title="Genres"
                bodyClasses={ 'select-list' }
                controls={ this._showControls() }
            >
                { facets.map( (genre, idx) =>
                {
                    return (
                        <div key={ idx }>
                            <label>
                                <input
                                    type="checkbox"
                                    value={ genre[0] }
                                    checked={ this.props.active.includes(genre[0]) }
                                    onChange={ () => this.toggleGenre(genre[0]) }
                                />
                                { genre[0] } ({ genre[1] })
                            </label>
                        </div>
                    );
                })}
            </Facet>
        )
    }
}

function mapStateToProps (state)
{
    return {
        active: state.currentFacets.genres.active
    }
}

const mapDispatchToProps = {
    // toggleFacetShowAll,
    addGenreToActive,
    removeGenreFromActive,
    clearActiveGenres,
    performGenreSearch
};

export default connect(mapStateToProps, mapDispatchToProps)(GenresFacet);
