import React from "react";

export const SourceResultType = ({result}) =>
{
    return (
        <div className="search-result">
            <h3>
                <a href={ result.url }>{ result.display_name_s }</a>
                <span className="result-type"> Source { result.public_images_b && <i className="fa fa-file-image-o" />}</span>
            </h3>
            <div>
                <div>{ result.archive_city_s }, { result.archive_s }</div>
                <div>{ result.source_type_s }{ result.date_statement_s ? `, ${result.date_statement_s}` : ""}{ result.surface_type_s ? `, ${result.surface_type_s}` : ""}.</div>
                <div>
                    { result.number_of_composers_i ? `${result.number_of_composers_i} composers inventoried. ` : " " }
                    { result.number_of_compositions_i ? `Contains ${result.number_of_compositions_i} pieces. ` : " " }
                </div>
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
                <div>{ result.composers_ssni && <Composers composers={ result.composers_ssni } /> }
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
                <a href={ result.url }>{ result.name_s } ({ result.siglum_s })</a>
                <span className="result-type"> Archive</span>
            </h3>
            <div>
                { result.city_s }, { result.country_s }.
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
