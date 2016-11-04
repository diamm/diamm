
/*
*   The Image Info Panel. Shows the contents of the page image
*   in sync with the Diva view.
* */
interface IImageSourceInfoProps
{
    children?: any;
}

export default function ImageSourceInfo ({
    children = null
}: IImageSourceInfoProps)
{
    return (
        <div id="source-body-image-source-info">
            <p>Source info</p>
        </div>
    );
}
