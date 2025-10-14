import {Dimension} from "../viewer-type-definitions";
import ImageManifest from "../image-manifest";

export default function getPageDimensions (pageIndex: number, manifest: ImageManifest): Dimension
{
    const dims = manifest.getMaxPageDimensions(pageIndex);

    return {
        width: Math.floor(dims.width),
        height: Math.floor(dims.height)
    };
}
