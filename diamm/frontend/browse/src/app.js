import React from 'react'; // eslint-disable-line no-unused-vars
import { render } from 'react-dom';
import { Provider } from 'react-redux'; // eslint-disable-line no-unused-vars
import { createStore } from 'redux';

import FilterContainer from './containers/filter';
import filter from './reducers/filter';


let store = createStore(filter);

render(
    <Provider store={store}>
        <div className="row">
        <FilterContainer />
        </div>
    </Provider>,
    document.getElementById('content-root')
);

