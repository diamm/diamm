import React from "react";
import ReactMarkdown from "react-markdown";
import { Link } from "react-router-dom";
import { IMAGES_ROUTE } from "../../routes";
import { CCM_NOTE_TYPE } from "../../constants";

/*
* React components for the Description tab. Factored out here
* to help simplify the Description class.
* */

export const ImageStatus = ({has_images, public_images, links}) =>
{
    // if the images are available, we don't need to show the message
    if (public_images === true)
        return false;

    let hasExternalImageLink = false;

    if (links !== null)
    {
        links.map((lnk, idx ) => {
            if (lnk.hasOwnProperty("url_type") && lnk.url_type === "External Images")
            {
                hasExternalImageLink = true;
            }
        });
    }

    if (has_images === false && public_images === false)
    {
        return (
            <tr>
                <th>Image Availability</th>
                <td>
                    DIAMM does not have images of this source.
                    { hasExternalImageLink ? `Please refer to the external links below for image availability.` : ``}
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
                    DIAMM has images of this manuscript but does not yet have permission to put them online.
                    { hasExternalImageLink ? ` Please refer to the external links below for image availability.` : ``}
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

export const NumberingSystemType = ({numbering_system_type}) =>
{
    if (!numbering_system_type)
        return null;

    return (
        <tr>
            <th>Numbering System</th>
            <td>{ numbering_system_type }</td>
        </tr>
    );
};

export const OtherIdentifiers = ({identifiers}) =>
{
    if (identifiers.length === 0)
        return null;

    return (
        <tr>
            <th>Other Identifiers</th>
            <td>
                <ul className="no-style">
                    { identifiers.map((identifier, idx) => {
                        return (
                            <li key={ idx }>
                                { identifier.identifier_type }: { identifier.identifier }
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
                                { entry.city &&
                                    <span>
                                        { entry.city }
                                        { entry.city_uncertain ? "?, " : ", " }
                                    </span>
                                }
                                { entry.region &&
                                <span>
                                        { entry.region }
                                    { entry.region_uncertain ? "? ": ", " }
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

export const Notes = ({notes, showEdit}) =>
{
    if (notes.length === 0)
        return null;

    return (
        <div className="notes">
            { notes.map( (note, idx) => {
                let thisNote, noteAuthor;

                if (note.hasOwnProperty('author') && note.author.indexOf('DIAMM') === -1 && note.author !== "None")
                {
                    noteAuthor = note.author;
                }
                else
                {
                    noteAuthor = "";
                }


                if (note.type === CCM_NOTE_TYPE)
                {
                    // Displays the CCM disclaimer before the note.
                    let disclaimer = "**This information is reproduced here by kind permission of the publishers. It is COPYRIGHT and copying/reproduction of any of this content without permission may result in legal action.**";
                    thisNote = `${disclaimer}\n\n${note.note}`;
                }
                else
                {
                    thisNote = `${note.note}`;
                }

                return (
                    <section key={ idx }>
                        <h5 className="title is-5">
                            { note.note_type }
                            { showEdit &&
                                <sup><a href={ `/admin/diamm_data/sourcenote/${note.pk}/` }>Edit</a></sup>
                            }
                        </h5>
                        <ReactMarkdown source={ thisNote } />
                        <div className="note-author">
                            { noteAuthor }
                        </div>
                    </section>
                );
            })}
        </div>
    );
};

export const CoverImage = ({show, info, authenticated}) =>
{
    if (!show)
        return null;

    let link = null;
    if (authenticated)
    {
        link = (<Link to={ {pathname: IMAGES_ROUTE, query: {p: info.label}} }>
            <img src={ `${info.url}full/350,/0/default.jpg` } />
        </Link>);
    }
    else
    {
        link = (<a href={ `/login/?next=${window.location.pathname}` }>
            <img src={ `${info.url}full/350,/0/default.jpg` } />
        </a>);
    }

    return (
        <figure className="card">
            <div className="card-image">
                <figure className="image">
                    { link }
                </figure>
            </div>
            <div className="card-content">
                <div className="content">
                    <p className="title is-5">{ info.label }</p>
                </div>
            </div>
        </figure>
    );
};

export const Contents = ({numInventoried, numComposers, uninventoried}) =>
{
    if (!numInventoried && !numComposers && !uninventoried)
        return null;

    let nums = "";

    if (numInventoried && numComposers)
    {
        nums += `${numInventoried} pieces from ${numComposers} composers. `
    }

    if (uninventoried)
    {
        nums += `Contains ${uninventoried} uninventoried works or miscellaneous sections.`
    }

    return (
        <tr>
            <th>Contents</th>
            <td>
                <span>{ nums }</span>
            </td>
        </tr>
    );
};

export const Archive = ({archive}) =>
{
    return (
        <tr>
            <th>Archive</th>
            <td>
                <a href={ archive.url }>{ archive.name }</a>, { archive.city }, { archive.country } ({ archive.siglum })
            </td>
        </tr>
    );
};

export const Shelfmark = ({shelfmark, name}) =>
{
    return (
        <tr>
            <th>Shelfmark</th>
            <td>
                { shelfmark } { name && <em>&ldquo;{ name }&rdquo;</em> }
            </td>
        </tr>
    );
};

export const Format = ({format}) =>
{
    if (!format)
        return null;

    return (
        <tr>
            <th>Format</th>
            <td>
                { format }
            </td>
        </tr>
    );
};

export const Measurements = ({measurements}) =>
{
    if (!measurements)
        return null;

    return (
        <tr>
            <th>Measurements</th>
            <td>
                { measurements }
            </td>
        </tr>
    );
};
