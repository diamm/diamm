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
import AnonymousFacet from "./anonymous_facet";
import OrganizationTypeFacet from "./organization_type_facet";
import CitiesFacet from "./cities_facet";

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

    _renderCitiesFacet ()
    {
        if (this.props.cities && this.props.cities.length > 0)
        {
            return (
                <CitiesFacet />
            )
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

    _renderAnonymousFacet ()
    {
        if (this.props.anonymous && this.props.anonymous.length > 0)
        {
            return (
                <AnonymousFacet />
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

    _renderOrganizationTypesFacet ()
    {
        if (this.props.organizationTypes && this.props.organizationTypes.length > 0)
        {
            return (
                <OrganizationTypeFacet
                    organization_types={ this.props.organizationTypes }
                    showAll={ this.props.showAllOrganizationTypes }
                />
            )
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

    _anySidebarBlockVisible ()
    {
        let vis = this.props.composers.length > 0 ||
                  this.props.genres.length > 0 ||
                  this.props.sourceTypes.length > 0 ||
                  this.props.anonymous.length > 0 ||
                  this.props.hasInventory.length > 0 ||
                  this.props.notations.length > 0 ||
                  this.props.cities.length > 0 ||
                  this.props.archiveLocations.length > 0 ||
                  this.props.organizationTypes.length > 0;
        return vis
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
                { this._anySidebarBlockVisible() ? <div className="filter-result-title">
                    Filter Results
                    </div> : "" }
                { this._renderComposersFacet() }
                { this._renderAnonymousFacet() }
                { this._renderNotationsFacet() }
                {/*{ this._renderCitiesFacet() }*/}
                { this._renderHasInventoryFacet() }
                { this._renderSourceTypeFacet() }
                { this._renderGenresFacet() }
                { this._renderArchiveLocationsFacet() }
                { this._renderOrganizationTypesFacet() }
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
        anonymous: state.results.facets.anonymous,
        genres: state.results.facets.genres,
        cities: state.results.facets.cities,
        showAllGenres: state.currentFacets.genres.showAll,
        organizationTypes: state.results.facets.organization_type,
        showAllOrganizationTypes: state.currentFacets.organizationTypes.showAll,

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
