import React, { PropTypes } from 'react'; // eslint-disable-line no-unused-vars
import TypeFilters from 'type_filters'; // eslint-disable-line no-unused-vars


const FilterBox = ({ types, onTypeClick }) =>
(
    <div className="FilterBox">
        <TypeFilters
            types={types}
            onTypeClick={onTypeClick}
        />
    </div>
);
FilterBox.propTypes =
{
    types: PropTypes.array.isRequired,
    onTypeClick: PropTypes.func.isRequired
};

export default FilterBox;
