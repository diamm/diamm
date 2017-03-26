import React from "react"
import { connect } from "react-redux";
import DebounceInput from "react-debounce-input";
import {
    updateCorrectionReportText,
    submitCorrectionReport
} from "../actions/corrections"


class Correction extends React.Component
{
    onCorrectionTextInput (text)
    {
        this.props.updateCorrectionReportText(text);
    }

    onSubmit ()
    {
        this.props.submitCorrectionReport(
            this.props.noteContents,
            this.props.sourcePK
        )
    }

    render ()
    {
        return (
            <div className="columns">
                <div className="column is-two-thirds content">
                    <p>Use this form to report a correction or contribute to the source record for <strong>{ this.props.sourceTitle }</strong>.
                        Your submission will be reviewed by DIAMM staff and, if accepted you will be acknowledged in the "Contributors"
                        section of the source record.
                    </p>
                    <DebounceInput
                        element="textarea"
                        forceNotifyByEnter={ false }
                        minLength={ 2 }
                        debounceTimeout={ 600 }
                        onChange={ event => this.onCorrectionTextInput(event.target.value) }
                        rows="7"
                        value={ this.props.noteContents }
                        className="textarea"
                    />
                    <p className="control is-pulled-right">
                        <button
                            className="button is-primary"
                            onClick={ () => this.onSubmit() }
                        >
                            Submit
                        </button>
                    </p>
                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        sourceTitle: state.source.display_name,
        sourcePK: state.source.pk,
        noteContents: state.corrections.noteContents
    };
}

export default connect(mapStateToProps, { updateCorrectionReportText, submitCorrectionReport })(Correction);
