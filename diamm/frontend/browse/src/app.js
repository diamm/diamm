var React = require('react');
var ReactDOM = require('react-dom');

const rootElement = document.getElementById('content-root');
const Foo = require('./components/foo.js').default;

let render = () =>
{
    ReactDOM.render(<Foo />, rootElement);
};

render();
