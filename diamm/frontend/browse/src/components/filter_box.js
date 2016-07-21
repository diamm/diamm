import React, { PropTypes } from 'react'; // eslint-disable-line no-unused-vars
import TypeFilters from './type_filters'; // eslint-disable-line no-unused-vars


const FilterBox = ({ type, onTypeClick }) =>
(
    <div className="FilterBox four columns">
        <TypeFilters
            active_type_filter={type}
            onTypeClick={onTypeClick}
        />
    </div>
);
FilterBox.propTypes =
{
    type: PropTypes.string.isRequired,
    onTypeClick: PropTypes.func.isRequired
};

export default FilterBox;
