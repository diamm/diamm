import React, { PropTypes } from 'react'; // eslint-disable-line no-unused-vars


const TypeFilter = ({ active, onTypeClick, type}) =>
(
    <li
        className={active ? 'type-filter active' : 'type-filter'}
        onClick={onTypeClick(type)}
    >
        {type}
    </li>
);
TypeFilter.propTypes =
{
    active: PropTypes.bool.isRequired,
    onTypeClick: PropTypes.func.isRequired,
    type: PropTypes.string.isRequired
};


const types = ['All', 'Sources', 'People', 'Places', 'Compositions'];
const TypeFilters = ({ active_type_filter, onTypeClick }) =>
(
    <ul className="filter">
        {types.map(type =>
            <TypeFilter
                active={type === active_type_filter}
                onTypeClick={onTypeClick}
                type={type}
            />
        )}
    </ul>
);
TypeFilters.propTypes =
{
    active_type_filter: PropTypes.string.isRequired,
    onTypeClick: PropTypes.func.isRequired
};

export default TypeFilters;
