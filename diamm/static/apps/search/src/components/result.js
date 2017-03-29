import React from "react";
import { connect } from "react-redux";
import {
    SourceResultType,
    PersonResultType,
    OrganizationResultType,
    CompositionResultType,
    ArchiveResultType,
    SetResultType
} from "./result_types";


class Result extends React.Component
{
    getResultType (result)
    {
        switch (result.type)
        {
            case ("source"):
                return <SourceResultType result={ result } />;
            case ("person"):
                return <PersonResultType result={ result } />;
            case ("organization"):
                return <OrganizationResultType result={ result } />;
            case ("composition"):
                return <CompositionResultType result={ result } />;
            case ("archive"):
                return <ArchiveResultType result={ result } />;
            case ("set"):
                return <SetResultType result={ result } />;
            default:
                return (<div>Type: { result.type }</div>);

        }
    }

    render ()
    {
        return this.getResultType(this.props.result);
    }
}

function mapStateToProps (state)
{
    return {};
}

export default connect(mapStateToProps)(Result);
