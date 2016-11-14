import React from "react";
import { connect } from "react-redux";

const Entry = ({entry}) =>
{
    return (
        <span dangerouslySetInnerHTML={{__html: entry.prerendered}} />
    );
}

const PrimaryStudy = ({entry}) =>
{
    return (
        <strong>
            { "\u2021" } <Entry entry={ entry } />
        </strong>
    );
};

class Bibliography extends React.Component
{
    render ()
    {
        const { bibliography } = this.props;
        return (
            <div className="row">
                <div className="sixteen columns source-bibliography">
                    <h3>Bibliography <small>&Dagger; <em>denotes primary source study</em></small></h3>
                    { bibliography.map( (entry, idx) => {
                        return (
                            <p key={ idx }>
                                { entry.primary_study ? <PrimaryStudy entry={ entry } /> : <Entry entry={ entry }/> }
                            </p>
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
        bibliography: state.source.bibliography
    }
}

export default connect(mapStateToProps)(Bibliography);
