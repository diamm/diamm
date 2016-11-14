import React from "react";
import { connect } from "react-redux";

const Sources = ({sources}) =>
{
    return (
        <div>
            <h5>Sources</h5>
            <ul>
                { sources.map( (source, idx) =>{
                    return (<li key={ idx }>
                        { source.display_name_s }
                    </li>);
                })}
            </ul>
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
                                <h4>{ set.cluster_shelfmark }</h4>
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
