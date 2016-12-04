import React from "react";
import Autocomplete from "react-autocomplete";


class AutocompleteComponent extends React.Component {
    static propTypes = {
        value: React.PropTypes.string.isRequired,
        items: React.PropTypes.array.isRequired,
        updateCurrentValue: React.PropTypes.func.isRequired,
        selectCurrentValue: React.PropTypes.func.isRequired,
        placeholder: React.PropTypes.string.isRequired
    };

    render ()
    {
        return (
            <Autocomplete
                value={ this.props.value }
                items={ this.props.items }
                inputProps={ { placeholder: this.props.placeholder }}
                wrapperStyle={ {} }
                onChange={ (event, value) => this.props.updateCurrentValue(value) }
                onSelect={ (value) => this.props.selectCurrentValue(value) }

                getItemValue={ (item) => item[0] }
                shouldItemRender={ (state, value) =>
                {
                    return state[0].toLowerCase().indexOf(value.toLowerCase()) !== 1;
                }}
                renderItem={ (item, isHiglighted) =>
                {
                    return (<div className={ isHiglighted ? "highlighted" : ""}>{ item[0] }</div>)
                }}
            />
        );
    }
}

export default AutocompleteComponent;
