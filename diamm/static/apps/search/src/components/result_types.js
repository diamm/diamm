import React from "react";

export const SourceResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.display_name_s }</a>
                <span className="result-type"> Source</span>
            </h3>
            <div>
                <div>{ result.archive_city_s }, { result.archive_s }</div>
            </div>

        </div>
    );
};

export const PersonResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.name_s }</a>
                <span className="result-type"> Person</span>
            </h3>
        </div>
    );
};

export const OrganizationResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.name_s }</a>
                <span className="result-type"> Organization</span>
            </h3>
        </div>
    );
};

export const CompositionResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.title_s }</a>
                <span className="result-type"> Composition</span>
            </h3>
            <div>
                <div>{ result.composers_ss && result.composers_ss.map( (c, i) =>{
                    return (
                        <span key={ i }>{ c }</span>
                    )
                    })}
                </div>
            </div>
        </div>
    );
};

export const ArchiveResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.name_s }</a>
                <span className="result-type"> Archive</span>
            </h3>
            <div>
                { result.city_s }, { result.country_s }
            </div>
        </div>
    );
};

export const SetResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.cluster_shelfmark_s }</a>
                <span className="result-type"> Set</span>
            </h3>
        </div>
    );
}
