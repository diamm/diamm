import React from "react"
import Header from "./header";


class App extends React.Component
{
    render ()
    {
        return (
            <div className="container">
                <Header />
                <div className="row">
                    <div className="sixteen columns">
                        { this.props.children }
                    </div>
                </div>
            </div>
        );
    }
}

export default App;
