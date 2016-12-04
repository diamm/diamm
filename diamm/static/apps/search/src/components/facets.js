import React from "react";
import _ from "lodash";
import Autocomplete from "react-autocomplete";

// for array indexes.
const FACET_NAME = 0;
const FACET_COUNT = 1;

function facetBlock (title, values, showAll, showAllClickHandler)
{
    // if there are no values to show, don't bother showing the facet block.
    if (_.isEmpty(values))
        return null;

    let facets = _.chunk(values, 2);

    if (!showAll)
        facets = facets.slice(0, 20);

    return (
        <div className="facet-block">
            <div className="facet-title">
                <h4>{ title }</h4>
                <div className="facet-show-control" onClick={ () => showAllClickHandler() }>
                    { showAll ? "Show fewer" : "Show all" }
                </div>
            </div>
            <div className="facet-body">
                { facets.map( (f, idx) => {
                    return (
                        <div key={ idx }>
                            <label><input type="checkbox" value={ f[FACET_NAME] } /> { f[FACET_NAME] } ({ f[FACET_COUNT] })</label>
                        </div>
                    );
                }) }
            </div>

        </div>
    )
}

export const GenresFacet = ({ genres, showAll, onShowAll }) =>
{
    return facetBlock(
        "Genres",
        genres,
        showAll,
        onShowAll
    );
};

export const ArchiveLocationsFacet = ({locations, onExpand, activeSelect, onReset}) =>
{
    // if there are no values to show, don't bother showing the facet block.
    if (_.isEmpty(locations))
        return null;

    let loc = locations;

    return (
        <div className="facet-block">
            <div className="facet-title">
                <h4>Archive Locations</h4>
                <div className="facet-show-control">
                    <a onClick={ () => onReset() }>Reset</a>
                </div>
            </div>
            <div className="facet-body">
                { _renderLocations(locations, onExpand, activeSelect) }
            </div>
        </div>
    );
};

function _renderLocations (locations, onExpand, activeSelect, parent=null)
{
    return locations.map( (loc, idx) =>
    {
        let children = null;
        if (activeSelect !== null && loc.pivot && loc.pivot.length > 0)
            children = _renderLocations(loc.pivot, onExpand, activeSelect, loc);

        return (
            <div key={ idx } className={ `archive-location-facet-${loc.field}` }>
                <label>
                    <input
                        type="radio"
                        name="archive-location"
                        checked={ activeSelect === loc.value }
                        onChange={ () => onExpand(loc.field, loc.value )}
                    />
                    { loc.value } ({ loc.count })</label>
                { children }
            </div>
        )
    });
}
