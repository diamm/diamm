import React from "react";
import { connect } from "react-redux";
import {
    toggleFacetShowAll,
    setArchiveLocationFacet,
    performArchiveLocationQuery,
    resetArchiveLocationFacet
} from "../actions/facets";

import {
    FACET_UPDATE_COMPOSER_TOGGLE,
    FACET_UPDATE_GENRE_TOGGLE,
    FACET_UPDATE_ARCHIVE_LOCATIONS_TOGGLE
} from "../constants";

import {
    GenresFacet,
    ArchiveLocationsFacet
} from "./facets";

import ComposerFacet from "./composer_facet";

import ResultCount from "./result_count";


class SideBar extends React.Component
{
    toggleShowAll (toggle, type)
    {
        this.props.toggleFacetShowAll(!toggle, type)
    }

    toggleArchiveLocations (activeType, activeSelect)
    {
        console.log(activeType, activeSelect);
        this.props.setArchiveLocationFacet(activeType, activeSelect);
        this.props.performArchiveLocationQuery(activeType, activeSelect);
    }

    resetArchiveLocations ()
    {
        this.props.resetArchiveLocationFacet();
    }

    render ()
    {
        if (!this.props.results)
        {
            return null;
        }

        return (
            <div className="facet-sidebar">
                <ResultCount count={ this.props.count } />
                <ComposerFacet />
                <GenresFacet
                    genres={ this.props.genres }
                    showAll={ this.props.showAllGenres }
                    onShowAll={ () => this.toggleShowAll(
                        this.props.showAllGenres,
                        FACET_UPDATE_GENRE_TOGGLE
                    ) }
                />
                <ArchiveLocationsFacet
                    locations={ this.props.archiveLocations }
                    onExpand={ this.toggleArchiveLocations.bind(this) }
                    onReset={ this.resetArchiveLocations.bind(this) }
                    activeSelect={ this.props.archiveActiveSelect }
                />
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        results: state.results,
        count: state.results.count,

        composers: state.results.facets.composers,
        showAllComposers: state.currentFacets.composers.show_all,

        genres: state.results.facets.genres,
        showAllGenres: state.currentFacets.genres.show_all,

        archiveLocations: state.results.facets.archive_locations,
        archiveActiveParent: state.currentFacets.archiveLocations.activeParent,
        archiveActiveSelect: state.currentFacets.archiveLocations.activeSelect
        // showAllArchiveLocations: state.currentFacets.archiveLocations.show_all
    };
}

const mapDispatchToProps = {
    toggleFacetShowAll,
    setArchiveLocationFacet,
    performArchiveLocationQuery,
    resetArchiveLocationFacet
};

export default connect(mapStateToProps, mapDispatchToProps)(SideBar);
