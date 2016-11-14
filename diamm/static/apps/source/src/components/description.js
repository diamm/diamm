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
    Notes
} from "./containers/description";


class Description extends React.Component
{
    render ()
    {
        const { archive } = this.props;

        return (
            <div className="row">
                <div className="eleven columns source-description">
                    <table className="source-details">
                        <tbody>
                        <tr>
                            <th>Archive</th>
                            <td>
                                <a href={ archive.url }>{ archive.name }</a>, { archive.city }, { archive.country } ({ archive.siglum })
                            </td>
                        </tr>
                        <tr>
                            <th>Shelfmark</th>
                            <td>
                                { this.props.shelfmark } { this.props.name && <em>&ldquo;{ this.props.name }&rdquo;</em> }
                            </td>
                        </tr>
                        <ImageStatus
                            has_images={ this.props.has_images }
                            public_images={ this.props.public_images }
                        />
                        <SurfaceType surface_type={ this.props.surface_type } />
                        <OtherIdentifiers indentifiers={ this.props.identifiers } />
                        <Notations notations={ this.props.notations } />
                        <InventoryProvided inventory_provided={ this.props.inventory_provided }/>
                        <Copyists copyists={ this.props.copyists } />
                        <Relationships relationships={ this.props.relationships } />
                        <Links links={ this.props.links } />
                        <Provenance provenance={ this.props.provenance } />
                        </tbody>
                    </table>

                    <Notes notes={ this.props.notes } />
                </div>
                <div className="five columns">
                    <img src="https://placehold.it/350x500" />
                </div>
            </div>
        );

    }
}

function mapStateToProps (state)
{
    return {
        shelfmark: state.source.shelfmark,
        name: state.source.name,
        archive: state.source.archive,
        has_images: state.source.has_images,
        public_images: state.source.public_images,
        surface_type: state.source.surface_type,
        identifiers: state.source.identifiers,
        notations: state.source.notations,
        inventory_provided: state.source.inventory_provided,
        copyists: state.source.copyists,
        relationships: state.source.relationships,
        links: state.source.links,
        provenance: state.source.provenance,
        notes: state.source.notes
    }
}

export default connect(mapStateToProps)(Description);
