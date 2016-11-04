import * as React from "react";

interface ITabContainerProps
{
    children?: any;
}

export default function TabContainer({
    children = null
}: ITabContainerProps)
{
    return (
        <div id="tab-container" className="sixteen columns">
            { children }
        </div>
    );
}
