import React from "react";

export const SourceResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3 className="title is-3">
                <a href={ result.url }>{ result.display_name }</a>
                <span className="result-type"> Source { result.public_images && <i className="fa fa-file-image-o" />}</span>
            </h3>
            <div>
                <div>{ result.archive_city }, { result.archive_name }</div>
                <div>{ result.source_type }{ result.date_statement ? `, ${result.date_statement }` : ""}{ result.surface ? `, ${result.surface }` : ""}</div>
                <div>
                    { result.number_of_composers ? `${result.number_of_composers} composers inventoried. ` : " " }
                    { result.number_of_compositions ? `Contains ${result.number_of_compositions} pieces. ` : " " }
                </div>
            </div>
        </div>
    );
};

export const PersonResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3 className="title is-3">
                <a href={ result.url }>{ result.name }</a>
                <span className="result-type"> Person</span>
            </h3>
        </div>
    );
};

export const OrganizationResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3 className="title is-3">
                <a href={ result.url }>{ result.name }</a>
                <span className="result-type"> Organization</span>
            </h3>
            <div>
                { result.location }
            </div>

        </div>
    );
};

export const CompositionResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.title }</a>
                <span className="result-type"> Composition</span>
            </h3>
            <div>
                <div>
                    { result.composers ? <Composers composers={ result.composers } /> : "Anonymous" }
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
                <a href={ result.url }>{ result.name } ({ result.siglum })</a>
                <span className="result-type"> Archive</span>
            </h3>
            <div>
                { result.city }, { result.country }.
            </div>
        </div>
    );
};

export const SetResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.cluster_shelfmark }</a>
                <span className="result-type"> Set</span>
            </h3>
            <div>
                <div>{ result.archives.join(", ") }</div>
                <div>{ result.sources.length } source{ result.sources.length > 1 ? "s" : ""}</div>
            </div>
        </div>
    );
};

/*
*
* Helper methods
**/
const Composers = ({composers}) =>
{
    return (
        <div>
            { composers.map( (composer, idx) => {
                let [ pk, full_name, uncertain ] = composer.split("|");
                return (
                    <span key={ idx } className="composer-names">
                        { full_name } { uncertain === "True" ? "(?) " : "" }
                    </span>
                );
            })}
        </div>
    );
};
