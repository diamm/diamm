import React from "react";
import { connect } from "react-redux";
import {
    ImageStatus,
    SurfaceType,
    OtherIdentifiers,
    Notations,
    InventoryProvided,
    Copyists,
    Relationships,
    Links,
    Provenance,
    Notes,
    CoverImage,
    Contents,
    Archive,
    Shelfmark,
    Format,
    Measurements,
    NumberingSystemType
} from "./containers/description";


class Description extends React.Component
{
    render ()
    {
        return (
            <div className="columns">
                <div className="column is-three-quarters">
                    <table className="source-details">
                        <tbody>
                            <Archive archive={ this.props.archive } />
                            <Shelfmark shelfmark={ this.props.shelfmark } name={ this.props.name } />
                            <ImageStatus
                                has_images={ this.props.has_images }
                                public_images={ this.props.public_images }
                                links={ this.props.links }
                            />
                            <SurfaceType surface_type={ this.props.surface_type } />
                            <NumberingSystemType numbering_system_type={ this.props.numbering_system_type } />
                            <Format format={ this.props.format } />
                            <Measurements measurements={ this.props.measurements } />
                            <OtherIdentifiers identifiers={ this.props.identifiers } />
                            <Notations notations={ this.props.notations } />
                            <InventoryProvided inventory_provided={ this.props.inventory_provided }/>
                            <Copyists copyists={ this.props.copyists } />
                            <Relationships relationships={ this.props.relationships } />
                            <Links links={ this.props.links } />
                            <Provenance provenance={ this.props.provenance } />
                            <Contents
                                numInventoried={ this.props.inventory.length }
                                numComposers={ this.props.composers.length }
                                uninventoried={ this.props.uninventoried.length } />
                        </tbody>
                    </table>

                    <Notes notes={ this.props.notes } showEdit={ this.props.userIsStaff } />
                </div>
                <div className="column">
                    <CoverImage
                        show={ this.props.cover_image_info && this.props.has_images && this.props.public_images }
                        info={ this.props.cover_image_info }
                        authenticated={ this.props.userIsAuthenticated }
                    />
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        display_name: state.source.display_name,
        shelfmark: state.source.shelfmark,
        name: state.source.name,
        archive: state.source.archive,
        has_images: state.source.has_images,
        public_images: state.source.public_images,
        open_images: state.source.open_images,
        surface_type: state.source.surface_type,
        numbering_system_type: state.source.numbering_system_type,
        identifiers: state.source.identifiers,
        notations: state.source.notations,
        inventory_provided: state.source.inventory_provided,
        copyists: state.source.copyists,
        relationships: state.source.relationships,
        links: state.source.links,
        provenance: state.source.provenance,
        notes: state.source.notes,
        cover_image_info: state.source.cover_image_info,
        uninventoried: state.source.uninventoried,
        inventory: state.source.inventory,
        composers: state.source.composer_inventory,
        source_type: state.source.source_type,
        date_statement: state.source.date_statement,
        type: state.source.type,
        pk: state.source.pk,
        format: state.source.format,
        measurements: state.source.measurements,

        userIsAuthenticated: state.user.isAuthenticated,
        userIsStaff: state.user.isStaff,
        username: state.user.username
    }
}

export default connect(mapStateToProps)(Description);
