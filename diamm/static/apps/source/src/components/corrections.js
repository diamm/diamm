import React from "react"
import { connect } from "react-redux";
import DebounceInput from "react-debounce-input";
import {
    updateCorrectionReportText,
    submitCorrectionReport
} from "../actions/corrections";

const ThankYou = ({submitted}) =>
{
    if (!submitted)
        return null;

    return (<div className="notification is-success">
        Your contribution has been sent for review. Thank you.
    </div>)
};



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
        // Prevent users from pulling up the correction view without being authenticated.
        // Redirects them to the login page.
        if (!this.props.userIsAuthenticated)
        {
            window.location = `/login/?next=${window.location.pathname}#/corrections`;
            return null;
        }

        return (
            <div className="columns">
                <div className="column is-two-thirds content">
                    <ThankYou submitted={ this.props.submitted } />
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
                        disabled={ this.props.submitting }
                    />
                    <p className="control is-pulled-right">
                        <button
                            ref="submitButton"
                            className="button is-primary"
                            onClick={ () => this.onSubmit() }
                            disabled={ this.props.submitting }
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
        noteContents: state.corrections.noteContents,
        submitted: state.corrections.submitted,
        submitting: state.corrections.submitting,
        userIsAuthenticated: state.user.isAuthenticated
    };
}

export default connect(mapStateToProps, { updateCorrectionReportText, submitCorrectionReport })(Correction);
