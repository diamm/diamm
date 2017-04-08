import React from "react";
import _ from "lodash";
import { connect } from "react-redux";
import Facet from "./facets";
import {
    toggleFacetShowAll
} from "../actions/facets"
import {
    addOrganizationToActive,
    removeOrganizationFromActive,
    clearActiveOrganizations,
    performOrganizationTypeSearch
} from "../actions/organization_type_facet";


class OrganizationTypeFacet extends React.Component
{
    toggleOrganizationType (value)
    {
        if (this.props.active.includes(value))
            this.deselectOrganizationType(value);
        else
            this.selectOrganizationType(value)
    }

    selectOrganizationType (value)
    {
        this.props.addOrganizationToActive(value);
        this.props.performOrganizationTypeSearch();
    }

    deselectOrganizationType (value)
    {
        this.props.removeOrganizationFromActive(value);
        this.props.performOrganizationTypeSearch();
    }

    clearActiveOrganizationTypes ()
    {
        this.props.clearActiveOrganizations();
        this.props.performOrganizationTypeSearch();
    }

    _showControls()
    {
        return (
            <div className="facet-show-control"
                 onClick={ () => this.clearActiveOrganizationTypes() }>
                Clear all
            </div>
        )
    }

    render()
    {
        let facets = _.chunk(this.props.organization_types, 2);
        return (
            <div>
                <Facet title="Organization Type"
                       bodyClasses={ 'select-list' }
                       controls={ this._showControls() }>
                    { facets.map( (orgtype, idx) =>
                    {
                        return (
                            <div key={ idx }>
                                <label>
                                    <input type="radio"
                                           name="organization-type"
                                           value={ orgtype[0] }
                                           checked={ this.props.active.includes(orgtype[0]) }
                                           onChange={ () => this.toggleOrganizationType(orgtype[0])}
                                    />
                                    { orgtype[0] } ({ orgtype[1] })
                                </label>
                            </div>
                        );
                    })}
                </Facet>
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        active: state.currentFacets.organizationTypes.active
    }
}

const mapDispatchToProps = {
    toggleFacetShowAll,
    addOrganizationToActive,
    removeOrganizationFromActive,
    clearActiveOrganizations,
    performOrganizationTypeSearch
};

export default connect(mapStateToProps, mapDispatchToProps)(OrganizationTypeFacet);