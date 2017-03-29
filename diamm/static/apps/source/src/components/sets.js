import React from "react";
import { connect } from "react-redux";

const Sources = ({sources}) =>
{
    return (
        <div className="source-set-sources">
            { sources.map( (source, idx) =>{
                let src;
                if (source.cover_image !== null)
                {
                    src = <img src={`${source.cover_image}full/100,/0/default.jpg` } />;
                }
                else
                {
                    src = (<div className="no-image">
                        <div>
                            <i className="fa fa-eye-slash" />
                        </div>
                        <div>
                            <small>No images available</small>
                        </div>
                    </div>)
                }

                return (
                    <div key={ idx } className="box">
                        <a href={ source.url }>
                            { src }
                        </a>

                        <figcaption>
                            <a href={ source.url }>{ source.display_name_s }</a>
                        </figcaption>
                    </div>
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
            <div className="columns">
                <div className="column source-sets">
                    { this.props.sets.map( (set, idx) =>{
                        return (
                            <div key={ idx }>
                                <h2 className="title is-3">Set: { set.cluster_shelfmark }</h2>
                                <h3 className="subtitle is-5"><strong>Type: </strong>{ set.set_type }</h3>
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
