import React from "react";
import {
    INVENTORY_ROUTE,
    INVENTORY_ROUTE_BY_COMPOSER,
    INVENTORY_ROUTE_ALPHABETICAL,
    IMAGES_ROUTE
} from "../../routes";
import { Link } from "react-router";
import { openQuickLookView } from "../../actions/index";
import { store } from "../../index";


const InventoryMenuItem = ({active, route, title, show=true}) =>
{
    if (!show)
        return null;

    return (
        <li className={ active ? "is-active" : ""}>
            <Link to={ route }>{ title }</Link>
        </li>
    );
};

export class InventoryMenu extends React.Component
{
    static contextTypes = {
        router: React.PropTypes.object
    };

    render()
    {
        let isActive = this.context.router.isActive;

        // a source is uninventoried if it has entries in the 'uninventoried' key AND it has no entries in the inventory.
        let isUninventoried = this.props.uninventoried.length > 0 && this.props.source_order.length === 0;

        return (
            <div className="tabs">
                <ul>
                    <InventoryMenuItem
                        active={ isActive(INVENTORY_ROUTE) }
                        route={ INVENTORY_ROUTE }
                        title={ isUninventoried ? "Uninventoried" : "Source Order" }
                        show={ this.props.source_order.length > 0 || isUninventoried }
                    />
                    <InventoryMenuItem
                        active={ isActive(INVENTORY_ROUTE_BY_COMPOSER) }
                        route={ INVENTORY_ROUTE_BY_COMPOSER }
                        title="By Composer (A-Z)"
                        show={ this.props.source_order.length > 0 }  // <-- don't bother showing the composers if there is nothing in the source.
                    />
                    <InventoryMenuItem
                        active={ isActive(INVENTORY_ROUTE_ALPHABETICAL) }
                        route={ INVENTORY_ROUTE_ALPHABETICAL }
                        title="By Composition (A-Z)"
                        show={ this.props.source_order.length > 0 }
                    />
                </ul>
            </div>
        );
    }
}

const onQuickLook = (url) =>
{
    store.dispatch(
        openQuickLookView(url)
    );
};


export const QuickLook = ({url}) =>
{
    if (!url)
        return null;

    return (
        <span className="icon is-small">
        <i
            className="fa fa-border fa-binoculars fa-small quicklook"
            onClick={ () => { onQuickLook(url) } }
        /></span>
    );
};

const linkComposerName = (composer) =>
{
    if (composer.url !== null)
    {
        return (
            <a href={ composer.url }>
                { composer.full_name }
            </a>
        );
    }
    else
    {
        return (
            composer.full_name
        );
    }
};

export const Composers = ({composers}) =>
{
    return (
        <div>
            { composers.map( (composer, idx) => {
                return (
                    <div key={ idx } className="composer-names">
                        { linkComposerName(composer) } { composer.uncertain ? "(?) " : " " }
                    </div>
                );
            })}
        </div>
    );
};

export const Foliation = ({folio_start, folio_end, show_quicklook}) =>
{
    if (!folio_start)
        return (
            <span>[no start folio listed]</span>
        );

    return (
        <span>
            { folio_start }{ (folio_end && folio_start !== folio_end) ? `–${folio_end} ` : " " }
            { show_quicklook &&
            <Link to={ {pathname: IMAGES_ROUTE, query: {p: folio_start}} }>
                <span className="icon is-small"><i className="fa fa-file-text-o fa-border quicklook" /></span>
            </Link>}
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
        <div>
            <h4>Item Bibliography</h4>
            { entry.map ( (bib, idx) => {
                return(
                    <p key={ idx } dangerouslySetInnerHTML={{__html: bib.prerendered_s }}/>
                );
            })}
        </div>
    );
};

export const ItemNotes = ({notes}) =>
{
    if (!notes)
        return null;

    return (
        <div>
            { notes.map( (note, idx) =>
            {
                return (
                    <div key={ idx }>
                        <h5>{ note.note_type }</h5>
                        <p>
                            { note.note }
                        </p>
                    </div>
                );
            })}
        </div>
    );
};

const Langs = ({langs}) =>
{
    return (
        <div>
            <strong>Languages: </strong>{ langs.join(", ") }
        </div>
    );
};

const Mensur = ({mensuration}) =>
{
    return (
        <div>
            <strong>Mensuration: </strong>{ mensuration }
        </div>
    );
};

const Clef = ({clef}) =>
{
    return (
        <div>
            <strong>Clef: </strong>{ clef }
        </div>
    );
};

const VoiceType = ({voicetype}) =>
{
    return (
        <div>
            <strong>Voice: </strong>{ voicetype }
        </div>
    );
};

const VoiceText = ({voicetext}) =>
{
    return (
        <div>
            <strong>Voice Text: </strong>{ voicetext }
        </div>
    );
};

export const Voices = ({voices, num_voices}) =>
{
    return (
        <div>
            <p className="is-bold">Voices</p>

            { num_voices &&
                <span><strong>Number of Voices:</strong> { num_voices }</span>}

            { voices && voices.map ( (voice, idx) => {
                return (
                    <div key={ idx } className="voice-detail">
                        { voice.voice_type_s && <VoiceType voicetype={ voice.voice_type_s } /> }
                        { voice.languages_ss && <Langs langs={ voice.languages_ss } /> }
                        { voice.mensuration_s && <Mensur mensuration={ voice.mensuration_s } /> }
                        { voice.clef_s && <Clef clef={ voice.clef_s }/> }
                        { voice.voice_text_s && <VoiceText voicetext={ voice.voice_text_s } /> }
                    </div>
                );
            })}
        </div>
    );
};

export const Attribution = ({attribution}) =>
{
    if (!attribution)
        return null;

    return (
        <div><strong>Source Attribution: </strong> { attribution }</div>
    )
};