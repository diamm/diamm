import React from "react";
import { connect } from "react-redux";

const Sources = ({sources}) =>
{
    return (
        <div className="source-set-sources">
            { sources.map( (source, idx) =>{
                let src="https://placehold.it/100x140";
                if (source.cover_image !== null)
                    src = `${source.cover_image}full/100,/0/default.jpg`;

                return (
                    <figure key={ idx } className="source-set-source">
                        <a href={ source.url }><img src={ src } /></a>
                        <figcaption>
                            <a href={ source.url }>{ source.display_name_s }</a>
                        </figcaption>
                    </figure>
                );
            })}
        </div>
    );
};


class Sets extends React.Component
{
    render ()
    {
        return (
            <div className="row">
                <div className="sixteen columns source-sets">
                    { this.props.sets.map( (set, idx) =>{
                        return (
                            <div key={ idx }>
                                <h2>Set: { set.cluster_shelfmark }</h2>
                                <p><strong>Type: </strong>{ set.set_type }</p>
                                <Sources sources={ set.sources } />
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        sets: state.source.sets
    }
}

export default connect(mapStateToProps)(Sets);
