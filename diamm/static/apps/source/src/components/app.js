import React from "react";
import { Link } from "react-router";
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
                <a href={ `/login/?next=${window.location.pathname}` }>Images (Log in to view)</a>
            </li>
        );
    }

    return <MenuLink active={ active } route={ route } title={ title } />;
};


class App extends React.Component
{
    static contextTypes = {
        router: React.PropTypes.object
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

        let isActive = this.context.router.isActive;

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
                                        active={ isActive(ROOT_ROUTE, true) }
                                        route={ ROOT_ROUTE }
                                        title="Description"
                                    />
                                    <MenuLink
                                        active={ isActive(INVENTORY_ROUTE, true) ||
                                                 isActive(INVENTORY_ROUTE_BY_COMPOSER, true) ||
                                                 isActive(INVENTORY_ROUTE_ALPHABETICAL, true) }
                                        route={ INVENTORY_ROUTE }
                                        title="Inventory"
                                        show={ this.props.source.inventory.length !== 0 || this.props.source.uninventoried.length !== 0 }
                                    />
                                    <ImagesMenuLink
                                        authenticated={ (this.props.user !== null && this.props.user.isAuthenticated) }
                                        active={ isActive(IMAGES_ROUTE, true) }
                                        route={ IMAGES_ROUTE }
                                        title="Images"
                                        show={
                                            this.props.source.public_images && this.props.source.has_images
                                        }
                                    />
                                    <MenuLink
                                        active={ isActive(SETS_ROUTE, true) }
                                        route={ SETS_ROUTE }
                                        title="Sets"
                                        show={ this.props.source.sets.length !== 0 }
                                    />
                                    <MenuLink
                                        active={ isActive(BIBLIOGRAPHY_ROUTE, true) }
                                        route={ BIBLIOGRAPHY_ROUTE }
                                        title="Bibliography"
                                        show={ this.props.source.bibliography.length !== 0 }
                                    />
                                    <MenuLink
                                        active={ isActive(COMMENTARY_ROUTE, true) ||
                                                 isActive(COMMENTARY_ROUTE_PRIVATE, true) }
                                        route={ COMMENTARY_ROUTE }
                                        title="Commentary"
                                    />
                                    <MenuLink
                                        active={ isActive(CONTRIBUTORS_ROUTE, true) }
                                        route={ CONTRIBUTORS_ROUTE }
                                        title="Contributors"
                                    />
                                </ul>
                                </div>
                            </div>
                            <div className="level-right">
                                <div className="tabs">
                                    <ul>
                                        <MenuLink
                                            active={ isActive(CORRECTIONS_ROUTE, true) }
                                            route={ CORRECTIONS_ROUTE }
                                            title="Contribute a Change"
                                            show={ this.props.userIsAuthenticated }
                                        />
                                        <ExternalMenuLink
                                            active={ false }
                                            route={ `${SERVER_BASE_URL}admin/diamm_data/source/${this.props.source.pk}` }
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
        user: state.user,
        userIsStaff: state.user.isStaff,
        userIsAuthenticated: state.user.isAuthenticated
    }
}

export default connect(mapStateToProps, { fetchSourceInfo, setUserInfo })(App);
