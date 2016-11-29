import React from "react";
import { connect } from "react-redux";
import Result from "./result";
import ResultCount from "./result_count";


class Results extends React.Component
{
    render ()
    {
        if (!this.props.results)
        {
            return null;
        }

        return (
            <div className="search-results">
                <ResultCount count={ this.props.count } />
                { this.props.results.map( (result) => {
                    return <Result result={ result } key={ result.id } />
                })}
            </div>
        )
    }
}

function mapStateToProps (state)
{
    return {
        results: state.results.results,
        count: state.results.count
    };
}

export default connect(mapStateToProps)(Results);
