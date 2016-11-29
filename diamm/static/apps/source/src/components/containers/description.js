import React from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router";
import { IMAGES_ROUTE } from "../../routes";

/*
* React components for the Description tab. Factored out here
* to help simplify the Description class.
* */

export const ImageStatus = ({has_images, public_images}) =>
{
    // if the images are available, we don't need to show the message
    if (public_images === true)
        return false;

    if (has_images === false && public_images === false)
    {
        return (
            <tr>
                <th>Image Availability</th>
                <td>
                    DIAMM does not have images of this source.
                </td>
            </tr>
        );
    }
    else if (has_images === true && public_images === false)
    {
        return (
            <tr>
                <th>Image Availability</th>
                <td>
                    DIAMM has images of this manuscript, but does not yet have permission to put them online.
                </td>
            </tr>
        );
    }
    else
    {
        return false;
    }
};


export const SurfaceType = ({surface_type}) =>
{
    if (!surface_type)
        return null;

    return (
        <tr>
            <th>Surface</th>
            <td>{ surface_type }</td>
        </tr>
    );
};

export const OtherIdentifiers = ({identifiers}) =>
{
    if (!identifiers)
        return null;

    return (
        <tr>
            <th>Other Identifiers</th>
            <td>
                <ul className="no-style">
                    { this.props.identifiers.map((identifier, idx) => {
                        return (
                            <li key={ idx }>
                                <strong>
                                    { identifier.identifier_type }:
                                </strong> { identifier.identifier }
                            </li>
                        );
                    })}
                </ul>
            </td>
        </tr>
    );
};

export const Notations = ({notations}) =>
{
    if (notations.length === 0)
        return null;

    return (
        <tr>
            <th>Notations</th>
            <td>
                <ul className="no-style">
                    { notations.map( (notation, idx) =>{
                        return (
                            <li key={ idx }>{ notation.name }</li>
                        );
                    })}
                </ul>
            </td>
        </tr>
    );
};

export const InventoryProvided = ({inventory_provided}) =>
{
    if (inventory_provided)
        return null;

    return (
        <tr>
            <th>Inventory</th>
            <td>This MS has not yet been inventoried by DIAMM. If you would like to submit an inventory, please send it to <a href="mailto:diamm@music.ox.ac.uk">diamm@music.ox.ac.uk</a></td>
        </tr>
    );
};

export const Copyists = ({copyists}) =>
{
    if (copyists.length === 0)
        return false;

    return (
        <tr>
            <th>Copyists</th>
            <td>
                <ul className="no-style">
                    { copyists.map( (copyist, idx) => {
                        return (
                            <li key={ idx }>
                                <a href={ copyist.copyist.url }>
                                    <span>
                                        { copyist.uncertain ? "? " : null }
                                        { copyist.copyist.name }
                                    </span>
                                </a> <span>({ copyist.type_s })</span>
                            </li>
                        );
                    })}
                </ul>
            </td>
        </tr>
    );
};

export const Relationships = ({relationships}) =>
{
    if (relationships.length === 0)
        return null;

    return (
        <tr>
            <th>Relationships</th>
            <td>
                <ul className="no-style">
                    { relationships.map( (relationship, idx) => {
                        return (
                            <li key={ idx }>
                                <a href={ relationship.related_entity.url }>
                                    { relationship.uncertain ? "? " : "" }
                                    { relationship.related_entity.name }
                                </a> <span>({ relationship.relationship_type })</span>
                            </li>
                        );
                    })}
                </ul>
            </td>
        </tr>
    );
};

export const Links = ({links}) =>
{
    if (links.length === 0)
        return null;

    return (
        <tr>
            <th>External Links</th>
            <td>
                <ul className="no-style">
                    { links.map( (link, idx) => {
                        return (
                            <li key={ idx }>
                                <a href={ link.link }>{ link.link_text }</a>
                            </li>
                        );
                    })}
                </ul>
            </td>
        </tr>
    );
};

export const Provenance = ({provenance}) =>
{
    if (provenance.length === 0)
        return null;

    return (
        <tr>
            <th>Provenance</th>
            <td>
                <ul className="no-style">
                    { provenance.map((entry, idx) => {
                        return (
                            <li key={ idx }>
                                { entry.entity &&
                                    <span>
                                        <a href={ entry.entity.url }>{ entry.entity.name }</a>
                                        { entry.entity_uncertain ? "?, " : ", " }
                                    </span>
                                }
                                { entry.protectorate &&
                                    <span>
                                        { entry.protectorate }
                                        { entry.protectorate_uncertain ? "?, ": ", " }
                                    </span>
                                }
                                { entry.region &&
                                    <span>
                                        { entry.region }
                                        { entry.region_uncertain ? "? ": ", " }
                                    </span>
                                }
                                { entry.city &&
                                    <span>
                                        { entry.city }
                                        { entry.city_uncertain ? "?, " : ", " }
                                    </span>
                                }
                                { entry.country &&
                                    <span>
                                        { entry.country }
                                        { entry.country_uncertain ? "? " : "" }
                                    </span>
                                }
                            </li>
                        );
                    })}
                </ul>
            </td>
        </tr>
    );
};

export const Notes = ({notes}) =>
{
    if (notes.length === 0)
        return null;

    return (
        <div>
            { notes.map( (note, idx) => {
                return (
                    <div key={ idx }>
                        <h4>{ note.note_type }</h4>
                        <ReactMarkdown source={ note.note } />
                        <hr />
                    </div>
                );
            })}
        </div>
    );
};

export const CoverImage = ({show, info}) =>
{
    if (!show)
        return null;

    return (
        <figure className="source-cover-image">
            <Link to={ IMAGES_ROUTE }>
                <img src={ `${info.url}/full/350,/0/default.jpg` } />
            </Link>
            <figcaption>{ info.label }</figcaption>
        </figure>
    );
};
