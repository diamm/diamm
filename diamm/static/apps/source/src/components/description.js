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
    Contents
} from "./containers/description";
import ProblemReport from "./problem_report";
import {
    openProblemReport
} from "../actions/problem_report";


class Description extends React.Component
{
    render ()
    {
        const { archive } = this.props;

        return (
            <div className="columns">
                <div className="column is-three-quarters">
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
                        <Contents
                            numInventoried={ this.props.inventory.length }
                            numComposers={ this.props.composers.length }
                            uninventoried={ this.props.uninventoried.length } />
                        </tbody>
                    </table>

                    <Notes notes={ this.props.notes } />
                    <div className="problem-report">
                        <div
                            className="button"
                            onClick={ () => this.props.openProblemReport() }
                        >
                            Report a problem
                        </div>
                    </div>
                    { this.props.userIsAuthenticated && this.props.problemReportVisible &&
                    <ProblemReport for={ this.props.display_name }
                                   type={ "source" }
                                   pk={ this.props.pk }
                                   username={ this.props.username }
                    /> }
                </div>
                <div className="column">
                    <CoverImage
                        show={ this.props.cover_image_info && this.props.has_images && this.props.public_images }
                        info={ this.props.cover_image_info }
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
        surface_type: state.source.surface_type,
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

        problemReportVisible: state.problem_report.visible,
        userIsAuthenticated: state.user.isAuthenticated,
        username: state.user.username
    }
}

export default connect(mapStateToProps, { openProblemReport })(Description);
