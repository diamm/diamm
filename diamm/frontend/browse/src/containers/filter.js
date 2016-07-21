import { connect } from 'react-redux';
import { setTypeFilter } from '../actions';
import FilterBox from '../components/filter_box';


const mapStateToProps = (state) =>
{
    return {
        type: state.type
    };
};


const mapDispatchToProps = (dispatch) =>
{
    return {
        onTypeClick: (type) =>
        {
            return () =>
            {
                dispatch(setTypeFilter(type));
            };
        }
    };
};


const FilterContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(FilterBox);

export default FilterContainer;
