import React from "react"
import _ from "lodash";


export class GenresFacet extends React.Component
{

    _showControls ()
    {
        return (
            <div
                className="facet-show-control"
                onClick={ () => showAllClickHandler() }
            >
                { this.props.showAll ? "Show fewer" : "Show all" }
            </div>
        )
    }

    render ()
    {
        let facets = _.chunk(this.props.genres, 2);

        if (!this.props.showAll)
            facets = facets.slice(0, 20);

        return (
            <Facet
                title="Genres"
                bodyClasses={ ['select-list'] }
                controls={ this._showControls() }
            >
                { this.props.genres.map( (genre, idx) =>
                {
                    return (
                        <div key={ idx }>
                            <label>
                                <input type="checkbox" value={ genre[0] }/>
                                { genre[0] } ({ genre[1] })
                            </label>
                        </div>
                    );
                })}
            </Facet>
        )
    }
}

