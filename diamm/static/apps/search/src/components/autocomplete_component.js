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
                items={ this.props.items.sort( (a, b) => { return a[0].toLowerCase().localeCompare(b[0].toLowerCase() )}) }
                inputProps={ { placeholder: this.props.placeholder, type: "text", className: "input" }}
                wrapperStyle={ {} }
                menuStyle={{
                    zIndex: 100,
                    borderRadius: '3px',
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.1)',
                    background: 'rgba(255, 255, 255, 0.9)',
                    padding: '2px 0',
                    fontSize: '90%',
                    position: 'fixed',
                    overflow: 'auto',
                    maxHeight: '50%',
                }}
                onChange={ (event, value) => this.props.updateCurrentValue(value) }
                onSelect={ (value) => this.props.selectCurrentValue(value) }

                getItemValue={ (item) => item[0] }
                shouldItemRender={ (item, value) =>
                {
                    return item[0].toLowerCase().indexOf(value.toLowerCase()) !== -1;
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
