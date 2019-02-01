import React from "react";
import { matchPath } from "react-router";
import { Link } from "react-router-dom";
import PropTypes from "prop-types";
import {
    ROOT_ROUTE,
    INVENTORY_ROUTE,
    INVENTORY_ROUTE_BY_COMPOSER,
    INVENTORY_ROUTE_ALPHABETICAL,
    INVENTORY_ROUTE_UNINVENTORIED,
    IMAGES_ROUTE,
    SETS_ROUTE,
    BIBLIOGRAPHY_ROUTE,
    CONTRIBUTORS_ROUTE,
    COMMENTARY_ROUTE,
    COMMENTARY_ROUTE_PRIVATE,
    CORRECTIONS_ROUTE
} from "../routes";

import { SERVER_BASE_URL } from "../constants";
import { connect } from "react-redux";

import Title from "./title";
import { fetchSourceInfo, setUserInfo } from "../actions/index";
import { isActive } from "../routes";

const MenuLink = ({active, route, title, show=true}) =>
{
    if (!show)
        return null;

    return (
        <li className={ active ? "is-active" : ""}>
            <Link to={ route }>{ title }</Link>
        </li>
    );
};

const ExternalMenuLink = ({active, route, title, show=true}) =>
{
    if (!show)
        return null;
    return (
        <li className={ active ? "is-active" : ""}>
            <a href={ route }>{ title }</a>
        </li>
    );
};

const ImagesMenuLink = ({authenticated, active, route, title, show=true}) =>
{
    // don't show the menu item if there are no images attached
    if (!show)
        return null;

    if (!authenticated)
    {
        return (
            <li className="unauthenticated-image-link">
                <a href={ `/login/?next=${window.location.pathname}%23/images` }>Images (Log in to view)</a>
            </li>
        );
    }

    return <MenuLink active={ active } route={ route } title={ title } />;
};

const ContributeMenuLink = ({authenticated, active, route, title, show=true}) =>
{
    if (!show)
        return null;

    if (!authenticated)
    {
        return (
            <li className="unauthenticated-contribute-link">
                <a href={ `/login/?next=${window.location.pathname}%23/corrections` }>Contribute a Change</a>
            </li>
        )
    }

    return <MenuLink active={ active } route={ route } title={ title } />;
};

class App extends React.Component
{
    static contextTypes = {
        router: PropTypes.object
    };

    componentWillMount ()
    {
        const parentElement = document.getElementById("source-body");
        const isAuthenticated = parentElement.getAttribute("data-is-authenticated");

        if (isAuthenticated === "True")
        {
            const isAuthenticated = parentElement.getAttribute("data-is-authenticated");
            const username = parentElement.getAttribute("data-username");
            const isStaff = parentElement.getAttribute("data-is-staff");
            const isSuperuser = parentElement.getAttribute("data-is-superuser");

            this.props.setUserInfo(username, isAuthenticated, isStaff, isSuperuser);
        }

        const sourceId = parentElement.getAttribute("data-source-id");
        this._sourceName = parentElement.getAttribute('data-source-name');
        // fire off request for source info
        this.props.fetchSourceInfo(sourceId);
    }

    render ()
    {
        if (!this.props.source)
        {
            return (
                <div>
                    <div className="loading-message">
                        <h5 className="title is-5">Loading { this._sourceName }</h5>
                    </div>
                    <div className="loading-spinner">
                        <div className="icon is-large">
                            <i className="fa fa-circle-o-notch fa-5x fa-spin" />
                        </div>
                    </div>
                </div>
            );        }

        // let isActive = this.context.router.isActive;
        return (
            <div>
                <Title />
                <div className="columns">
                    <div className="column">
                        <div className="level">
                            <div className="level-left is-fullwidth">
                                <div className="tabs">
                                <ul className="source-section-selector">
                                    <MenuLink
                                        active={ isActive(location.hash, ROOT_ROUTE) }
                                        route={ ROOT_ROUTE }
                                        title="Description"
                                    />
                                    <MenuLink
                                        active={ isActive(location.hash, INVENTORY_ROUTE) ||
                                                 isActive(location.hash, INVENTORY_ROUTE_BY_COMPOSER) ||
                                                 isActive(location.hash, INVENTORY_ROUTE_ALPHABETICAL) }
                                        route={ INVENTORY_ROUTE }
                                        title="Inventory"
                                        show={ this.props.source.inventory.length !== 0 || this.props.source.uninventoried.length !== 0 }
                                    />
                                    <ImagesMenuLink
                                        authenticated={ (this.props.user !== null && this.props.user.isAuthenticated) }
                                        active={ isActive(location.hash, IMAGES_ROUTE) }
                                        route={ IMAGES_ROUTE }
                                        title="Images"
                                        show={
                                            this.props.source.public_images && this.props.source.has_images
                                        }
                                    />
                                    <MenuLink
                                        active={ isActive(location.hash, SETS_ROUTE) }
                                        route={ SETS_ROUTE }
                                        title="Sets"
                                        show={ this.props.source.sets.length !== 0 }
                                    />
                                    <MenuLink
                                        active={ isActive(location.hash, BIBLIOGRAPHY_ROUTE) }
                                        route={ BIBLIOGRAPHY_ROUTE }
                                        title="Bibliography"
                                        show={ this.props.source.bibliography.length !== 0 }
                                    />
                                    <MenuLink
                                        active={ isActive(location.hash, COMMENTARY_ROUTE) ||
                                                 isActive(location.hash, COMMENTARY_ROUTE_PRIVATE) }
                                        route={ COMMENTARY_ROUTE }
                                        title="Commentary"
                                    />
                                    <MenuLink
                                        active={ isActive(location.hash, CONTRIBUTORS_ROUTE) }
                                        route={ CONTRIBUTORS_ROUTE }
                                        title="Contributors"
                                    />
                                </ul>
                                </div>
                            </div>
                            <div className="level-right">
                                <div className="tabs">
                                    <ul>
                                        <ContributeMenuLink
                                            authenticated={ (this.props.user !== null && this.props.user.isAuthenticated) }
                                            active={ isActive(location.hash, CORRECTIONS_ROUTE) }
                                            route={ CORRECTIONS_ROUTE }
                                            title="Contribute a Change"
                                        />
                                        <ExternalMenuLink
                                            active={ false }
                                            route={ `${SERVER_BASE_URL}/admin/diamm_data/source/${this.props.source.pk}` }
                                            title="Edit"
                                            show={ this.props.userIsStaff }
                                        />
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                { this.props.children }
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        source: state.source,
        location: state.router.location,
        user: state.user,
        userIsStaff: state.user.isStaff,
        userIsAuthenticated: state.user.isAuthenticated
    }
}

export default connect(mapStateToProps, { fetchSourceInfo, setUserInfo })(App);
