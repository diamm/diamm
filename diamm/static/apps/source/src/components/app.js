import React from "react";
import { Link } from "react-router";
import {
    ROOT_ROUTE,
    INVENTORY_ROUTE,
    INVENTORY_ROUTE_BY_COMPOSER,
    INVENTORY_ROUTE_ALPHABETICAL,
    IMAGES_ROUTE,
    SETS_ROUTE,
    BIBLIOGRAPHY_ROUTE,
    CREDITS_ROUTE,
    COMMENTARY_ROUTE
} from "../routes";
import { connect } from "react-redux";

import Title from "./title";
import { fetchSourceInfo, setUserInfo } from "../actions/index";

const MenuLink = ({active, route, title, show=true}) =>
{
    if (!show)
        return null;

    return (
        <li className={ active ? "active" : ""}>
            <Link to={ route }>{ title }</Link>
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
                Images (<a href={ `/login?next=${route}` }>Log in to view</a>)
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
        // fire off request for source info
        this.props.fetchSourceInfo(sourceId);
    }

    render ()
    {
        if (!this.props.source)
        {
            return (
                <div className="loading-spinner">
                    <i className="fa fa-2x fa-spinner fa-spin" />
                    <span className="message">Loading...</span>
                </div>
            );
        }

        let isActive = this.context.router.isActive;

        return (
            <div>
                <Title />
                <div className="row">
                    <ul className="source-section-selector">
                        <MenuLink
                            active={ isActive(ROOT_ROUTE, true) }
                            route={ ROOT_ROUTE }
                            title="Description"
                        />
                        <MenuLink
                            active={ isActive(INVENTORY_ROUTE, true) || isActive(INVENTORY_ROUTE_BY_COMPOSER, true) || isActive(INVENTORY_ROUTE_ALPHABETICAL) }
                            route={ INVENTORY_ROUTE }
                            title="Inventory"
                            show={ this.props.source.inventory.length !== 0 }
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
                            active={ isActive(COMMENTARY_ROUTE, true) }
                            route={ COMMENTARY_ROUTE }
                            title="Commentary"
                            show={ false }
                        />
                        <MenuLink
                            active={ isActive(CREDITS_ROUTE, true) }
                            route={ CREDITS_ROUTE }
                            title="Credits"
                            show={ false }
                        />
                    </ul>
                </div>
                <div className="row source-data">
                    { this.props.children }
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        source: state.source,
        user: state.user
    }
}

export default connect(mapStateToProps, { fetchSourceInfo, setUserInfo })(App);
