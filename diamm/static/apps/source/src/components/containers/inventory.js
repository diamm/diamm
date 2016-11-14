import React from "react";
import {
    INVENTORY_ROUTE,
    INVENTORY_ROUTE_BY_COMPOSER,
    INVENTORY_ROUTE_ALPHABETICAL
} from "../../routes";
import { Link } from "react-router";


export class InventoryMenu extends React.Component
{
    static contextTypes = {
        router: React.PropTypes.object
    };

    render()
    {
        let isActive = this.context.router.isActive;

        return (
            <ul className="source-inventory-menu">
                <li>View: </li>
                <li className={ isActive(INVENTORY_ROUTE) ? "active" : ""}>
                    <Link to={ INVENTORY_ROUTE }>Source Order</Link>
                </li>
                <li className={ isActive(INVENTORY_ROUTE_BY_COMPOSER) ? "active" : ""}>
                    <Link to={ INVENTORY_ROUTE_BY_COMPOSER }>By Composer (A-Z)</Link>
                </li>
                <li className={ isActive(INVENTORY_ROUTE_ALPHABETICAL) ? "active" : ""}>
                    <Link to={ INVENTORY_ROUTE_ALPHABETICAL }>Alphabetical by Composition</Link>
                </li>
            </ul>
        );
    }
}

const onQuickLook = (url) =>
{
    console.log('quicklook ', url);
};

export const QuickLook = ({url}) =>
{
    return (
        <span
            className="fa fa-border fa-binoculars quicklook"
            onClick={ () => onQuickLook(url) }
        />
    );
};

export const Composers = ({composers}) =>
{
    return (
        <div>
            { composers.map( (composer, idx) => {
                return (
                    <span key={ idx } className="composer-names">
                        { composer.full_name } { composer.uncertain ? "(?) " : "" }
                        <QuickLook url={ composer.url } />
                    </span>
                );
            })}
        </div>
    );
};

export const Foliation = ({folio_start, folio_end, show_quicklook}) =>
{
    return (
        <span>
            { folio_start }{ (folio_end && folio_start !== folio_end) ? `–${folio_end} ` : " " }
            { show_quicklook &&
                <i className="fa fa-eye fa-border quicklook" />}
        </span>
    );
};

export const Genres = ({genres}) =>
{
    if (!genres)
        return null;

    return (
        <span>
            <strong>Genres: </strong> { genres.join(", ") }
        </span>
    );
};

export const Bibliography = ({entry}) =>
{
    if (!entry)
        return null;

    return (
        <span>
            <p><strong>Item Bibliography</strong></p>
            { entry.map ( (bib, idx) => {
                return(
                    <p key={ idx } dangerouslySetInnerHTML={{__html: bib.prerendered_s }}/>
                );
            })}
        </span>
    );
};

export const Voices = ({voices, num_voices}) =>
{
    return (
        <div>
            { num_voices &&
                <span><strong>Number of Voices:</strong> { num_voices }</span>}

            { voices.map ( (voice, idx) => {
                return (
                    <div key={ idx } className="voice-detail">
                        <ul>
                            { voice.voice_type_s &&
                                <li><strong>Voice: </strong>{ voice.voice_type_s }</li>}
                            { voice.languages_ss &&
                                <li><strong>Languages: </strong>{ voice.languages_ss.join(", ") }</li>}
                            { voice.mensuration_s &&
                                <li><strong>Mensuration: </strong>{ voice.mensuration_s }</li> }
                            { voice.clef_s &&
                                <li><strong>Clef: </strong>{ voice.clef_s }</li>}
                        </ul>
                        { voice.voice_text_s &&
                            <span><strong>Voice text: </strong> { voice.voice_text_s }</span>}

                    </div>
                );
            })}
        </div>
    );
};

export const Details = ({genres, voices, num_voices, bibliography}) =>
{
    if (!genres && !voices && !num_voices && !bibliography)
        return null;

    return (
        <tr>
            <td />
            <td className="item-details">
                <Genres genres={ genres }/>
                <Voices voices={ voices } num_voices={ num_voices } />
            </td>
            <td className="item-bibliography">
                <Bibliography entry={ bibliography } />
            </td>
        </tr>
    );
};
