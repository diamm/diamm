import React from "react";
import { connect } from "react-redux";
import Facet from "./facets";
import _ from "lodash";
import {
    performAnonymousSearch,
    updateAnonymousValue,
    clearAnonymousValue
} from "../actions/anonymous_facet";


class AnonymousFacet extends React.Component
{
    selectAnonymousValue (value)
    {
        this.props.updateAnonymousValue(value);
        this.props.performAnonymousSearch();
    }

    clearAnonymous ()
    {
        this.props.clearAnonymousValue();
        this.props.performAnonymousSearch();
    }

    _showControls ()
    {
        return (
            <div
                className="facet-show-control"
                onClick={ () => this.clearAnonymous() }
            >
                Clear
            </div>
        )
    }

    render ()
    {
        let facets = _.chunk(this.props.anonymousFacet, 2);
        return (
            <Facet
                title="Anonymous Compositions"
                bodyClasses={ 'select-list' }
                controls={ this._showControls() }
            >
                { facets.map( (facet, idx) =>
                {
                    return (
                        <div key={ idx }>
                            <label>
                                <input
                                    type="radio"
                                    name="anonymous"
                                    checked={ this.props.activeSelect === facet[0] }
                                    onChange={ () => this.selectAnonymousValue(facet[0])}
                                />
                                { facet[0] === "true" ? "Yes" : "No" }
                            </label>
                        </div>
                    );
                })}
            </Facet>
        );
    }
}

function mapStateToProps (state)
{
    return {
        anonymousFacet: state.results.facets.anonymous,
        activeSelect: state.currentFacets.anonymous.active
    };
}

const mapDispatchToProps = {
    performAnonymousSearch,
    updateAnonymousValue,
    clearAnonymousValue
};

export default connect(mapStateToProps, mapDispatchToProps)(AnonymousFacet);
