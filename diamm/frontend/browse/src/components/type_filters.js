import React, { PropTypes } from 'react'; // eslint-disable-line no-unused-vars


const TypeFilter = ({ type, active, onTypeClick }) =>
(
    <li
        className="type-filter"
        onClick={onTypeClick}
    >
        {type}
    </li>
);
TypeFilter.propTypes =
{
    type: PropTypes.string.isRequired,
    active: PropTypes.bool.isRequired,
    onTypeClick: PropTypes.func.isRequired
};


const TypeFilters = ({ types, onTypeClick }) =>
(
    <ul>
        {types.map(type =>
            <TypeFilter
                type={type.name}
                active={type.active}
                onTypeClick={() => onTypeClick(type.name)}
            />
        )}
    </ul>
);
TypeFilters.propTypes =
{
    types: PropTypes.array.isRequired,
    onTypeClick: PropTypes.func.isRequired
};

export default TypeFilters;
