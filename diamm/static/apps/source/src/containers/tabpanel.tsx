import * as React from "react";
import { Link } from "react-router";

interface ITabPanelProps {
    title: string;
    route: string;
    id?: string;
    children?: any;
    isDefault?: boolean;
}

export default function TabPanel ({
    title = "",
    route = "",
    id = "",
    children = null,
    isDefault = false
}: ITabPanelProps)
{
    return (
        <div id={ id }>
            <div className="source-tabs">
                <Link to={ route }>{ title }</Link>
            </div>
            { children }
        </div>
    );
}
