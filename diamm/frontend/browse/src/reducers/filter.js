const default_state =
{
    type: 'All'
};

const filter = (state = default_state, action) =>
{
    switch (action.type)
    {
        case 'SET_TYPE_FILTER':
            return Object.assign({}, state,
                {
                    type: action.type_filter
                })
        default:
            return state;
    }
};

export default filter;
