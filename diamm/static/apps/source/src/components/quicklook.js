import React from "react";
import _ from "lodash";
import { connect } from "react-redux";
import { closeQuickLookView } from "../actions";

const QLLabelledContent = ({label, content}) =>
{
    if (!content)
        return null;

    return (
        <p>
            <strong>{ label }: </strong>
            { content }
        </p>
    )
};

const QLCompositionRenderer = (content) =>
{
    return (
        <div>Composition</div>
    );
};

const QLComposerRenderer = (content) =>
{
    return (
        <div>
            <div>
                <QLLabelledContent
                    label="Other names"
                    content={ content.variant_names.join(", ") }
                />
            </div>
            <h4>Other Compositions</h4>
            <table>
                <thead>
                    <tr>
                        <th>Composition</th>
                        <th>Appears in</th>
                    </tr>
                </thead>
                <tbody>
                    { content.compositions.map( (cmp, idx) =>
                    {
                        return (
                            <tr key={ idx }>
                                <td>
                                    <a href={ cmp.url } target="_blank">
                                        { cmp.title }
                                    </a> { cmp.uncertain ? "?" : "" }
                                </td>
                                <td>
                                    { cmp.sources.map( (src, idx2) =>
                                    {
                                        return (
                                            <span key={ idx2 }>
                                                <a href={ src.url } target="_blank">
                                                    { src.name }
                                                </a> </span>
                                        );
                                    })}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};


class QuickLook extends React.Component
{
    componentDidMount()
    {
        document.body.style.overflow = "hidden";
    }

    componentWillUnmount()
    {
        document.body.style.overflow = "auto";
    }

    onCloseQuickLook ()
    {
        this.props.closeQuickLookView();
    }

    getQLRenderer (content)
    {
        // selects the appropriate renderer based on the content
        switch (content.type)
        {
            case ("person"):
                return QLComposerRenderer(content);
            case ("composition"):
                return QLCompositionRenderer(content)
            default:
                return content.type;
        }
    }

    render ()
    {
        if (_.isEmpty(this.props.content))
            return null;

        return (
            <div className="modal" style={ {width: "100%" } }>
                <div className="modal-background" />
                <div className="modal-card">
                    <header className="modal-card-head">
                        <div>
                            QuickLook: { this.props.content.title || this.props.content.full_name }
                        </div>
                        <button className="delete" />
                    </header>
                    <section className="modal-card-body">
                        { this.getQLRenderer(this.props.content) }
                    </section>
                </div>
            </div>
        );
    }
}

export default connect(null, { closeQuickLookView })(QuickLook);
