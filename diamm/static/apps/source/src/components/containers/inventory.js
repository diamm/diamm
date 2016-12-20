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
        let isUninventoried = this.props.uninventoried.length > 0;

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
        <span
            className="fa fa-border fa-binoculars quicklook"
            onClick={ () => { onQuickLook(url) } }
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
                        <QuickLook
                            url={ composer.url }
                        />
                    </span>
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
                <i className="fa fa-file-text-o fa-border quicklook" />
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
        <span>
            <div><strong>Item Bibliography</strong></div>
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

            { voices && voices.map ( (voice, idx) => {
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

export const Attribution = ({attribution}) =>
{
    if (!attribution)
        return null;

    return (
        <div><strong>Source Attribution: </strong> { attribution }</div>
    )
};
