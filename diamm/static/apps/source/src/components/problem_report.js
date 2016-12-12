import React from "react";
import { connect } from "react-redux";
import {
    closeProblemReport,
    updateProblemReportText
} from "../actions/problem_report";
import DebounceInput from "react-debounce-input";


class ProblemReport extends React.Component
{
    componentDidMount()
    {
        document.body.style.overflow = "hidden";
    }

    componentWillUnmount()
    {
        document.body.style.overflow = "auto";
    }

    onCloseProblemReport ()
    {
        this.props.closeProblemReport();
    }

    storeNoteInState(event)
    {
        this.props.updateProblemReportText(event.target.value);
    }

    render()
    {
        return (
            <div className="modal is-active">
                <div className="modal-background" />
                <div className="modal-card">
                    <header className="modal-card-head">
                        <p className="modal-card-title">Report a problem with { this.props.for }</p>
                        <button
                            className="fa fa-close"
                            onClick={ () => this.onCloseProblemReport() }
                        />
                    </header>

                    <section className="modal-card-body">
                        <div>
                            <p>Note: You can close this window if you need to consult the record before submitting,
                                and your text will be saved. Just click the "report a problem" button again to resume.</p>
                        </div>
                        <div>
                            <label className="label">Describe the problem</label>
                            <p className="control">
                                <DebounceInput
                                    element="textarea"
                                    forceNotifyByEnter={false}
                                    minLength={ 2 }
                                    debounceTimeout={ 600 }
                                    onChange={ event => this.storeNoteInState(event) }
                                    rows="7"
                                    value={ this.props.noteContents }
                                    className="textarea"
                                />
                            </p>
                        </div>
                    </section>
                    <footer className="modal-card-foot">
                        <div>Submitted by { this.props.username }</div>
                        <button className="button is-primary">Submit</button>
                    </footer>

                </div>
            </div>
        );
    }
}

function mapStateToProps (state)
{
    return {
        noteContents: state.problem_report.noteContents
    }
}

export default connect(mapStateToProps, { closeProblemReport, updateProblemReportText })(ProblemReport);
