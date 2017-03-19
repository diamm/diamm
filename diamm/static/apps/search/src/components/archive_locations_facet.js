import React from "react";
import { connect } from "react-redux";
import _ from "lodash";
import Facet from "./facets";
import {
    setArchiveLocationFacet,
    performArchiveLocationQuery,
    resetArchiveLocationFacet
} from "../actions/facets"


class ArchiveLocationsFacet extends React.Component
{
    toggleArchiveLocations (activeType, activeSelect)
    {
        this.props.setArchiveLocationFacet(activeType, activeSelect);
        this.props.performArchiveLocationQuery(activeType, activeSelect);
    }

    resetArchiveLocations ()
    {
        this.props.resetArchiveLocationFacet();
    }

    _renderLocations (locations, onExpand, activeSelect, parent=null)
    {
        return locations.map( (loc, idx) =>
        {
            let children = null;
            if (activeSelect !== null && loc.pivot && loc.pivot.length > 0)
                children = this._renderLocations(loc.pivot, onExpand, activeSelect, loc);

            return (
                <div key={ idx } className={ `archive-location-facet-${loc.field}` }>
                    <label>
                        <input
                            type="radio"
                            name="archive-location"
                            checked={ activeSelect === loc.value }
                            onChange={ () => onExpand(loc.field, loc.value)}
                        />
                        { loc.value } ({ loc.count })</label>
                    { children }
                </div>
            )
        });
    }

    _showControls ()
    {
        return (
            <div className="facet-show-control"
                 onClick={ () => this.resetArchiveLocations() }>
                Reset
            </div>
        );
    }

    render ()
    {
        // if there are no values to show, don't bother showing the facet block.
        if (_.isEmpty(this.props.locations))
            return null;

        return (
            <Facet
                title="Archives"
                controls={ this._showControls() }
                bodyClasses={ 'select-list' }
            >
                { this._renderLocations(
                    this.props.locations,
                    this.toggleArchiveLocations.bind(this),
                    this.props.activeSelect)
                }
            </Facet>
        );
    }
}

const mapDispatchToProps = {
    setArchiveLocationFacet,
    performArchiveLocationQuery,
    resetArchiveLocationFacet
};

export default connect(null, mapDispatchToProps)(ArchiveLocationsFacet);
