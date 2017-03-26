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
            <div className="columns">
                <div className="column source-bibliography content">
                    <p><strong>&Dagger; <em>denotes primary source study</em></strong></p>
                    { bibliography.map( (entry, idx) => {
                        return (
                            <p key={ idx } className="bibliography-entry">
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
