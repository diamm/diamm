import React from "react";
import { connect } from "react-redux";
import {
    toggleFacetShowAll,
    setArchiveLocationFacet,
    performArchiveLocationQuery,
    resetArchiveLocationFacet
} from "../actions/facets";

import {
    FACET_UPDATE_ARCHIVE_LOCATIONS_TOGGLE
} from "../constants";

import ArchiveLocationsFacet from "./archive_locations_facet";
import ComposerFacet from "./composer_facet";
import GenresFacet from "./genres_facet";
import NotationsFacet from "./notations_facet";
import SourceTypeFacet from "./source_type_facet";
import HasInventoryFacet from "./has_inventory_facet";

import ResultCount from "./result_count";


class SideBar extends React.Component
{

    _renderArchiveLocationsFacet ()
    {
        if (this.props.archiveLocations && this.props.archiveLocations.length > 0)
        {
            return (
                <ArchiveLocationsFacet
                    locations={ this.props.archiveLocations }
                    activeSelect={ this.props.archiveActiveSelect }
                />
            )
        }
    }

    _renderNotationsFacet ()
    {
        if (this.props.notations && this.props.notations.length > 0)
        {
            return (
                <NotationsFacet />
            );
        }
    }

    _renderHasInventoryFacet ()
    {
        if (this.props.hasInventory && this.props.hasInventory.length > 0)
        {
            return (
                <HasInventoryFacet />
            )
        }
    }

    _renderSourceTypeFacet ()
    {
        if (this.props.sourceTypes && this.props.sourceTypes.length > 0)
        {
            return (
                <SourceTypeFacet />
            );
        }
    }

    _renderGenresFacet ()
    {
        if (this.props.genres && this.props.genres.length > 0)
        {
            return (
                <GenresFacet
                    genres={ this.props.genres }
                    showAll={ this.props.showAllGenres }
                />
            );
        }
    }

    _renderComposersFacet ()
    {
        if (this.props.composers && this.props.composers.length > 0)
        {
            return (
                <ComposerFacet />
            );
        }
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
                { this._renderComposersFacet() }
                { this._renderNotationsFacet() }
                { this._renderHasInventoryFacet() }
                { this._renderSourceTypeFacet() }
                { this._renderGenresFacet() }
                { this._renderArchiveLocationsFacet() }
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
        notations: state.results.facets.notations,
        sourceTypes: state.results.facets.source_type,
        hasInventory: state.results.facets.has_inventory,

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
