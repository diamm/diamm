import React from "react";
import { connect } from "react-redux"
import { Genres, Voices, Bibliography, Attribution } from "./containers/inventory";


class Details extends React.Component
{
    render ()
    {
        const {
            genres,
            voices,
            num_voices,
            bibliography,
            source_attribution
        } = this.props.entry;

        if (!genres && !voices && !num_voices && !bibliography)
            return null;

        return (
            <div className="row">
                <div className="voice-details three columns">
                    <Voices voices={ voices } num_voices={ num_voices } />
                </div>
                <div className="item-details three columns">
                    <Genres genres={ genres }/>
                    <Attribution attribution={ source_attribution } />
                </div>
                <div className="item-bibliography ten columns">
                    <Bibliography entry={ bibliography } />
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
    }
}

export default connect(mapStateToProps)(Details);

