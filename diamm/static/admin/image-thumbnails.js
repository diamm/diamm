"use strict";

let imageListPreview = null;
let imageListPreviewLink = null;

function hideImageListPreview() {
    if (imageListPreview) {
        imageListPreview.hidden = true;
    }
    imageListPreviewLink = null;
}

function positionImageListPreview() {
    if (!imageListPreviewLink || !imageListPreview) {
        return;
    }
    const rect = imageListPreviewLink.getBoundingClientRect();
    const width = imageListPreview.offsetWidth;
    const height = imageListPreview.offsetHeight;
    let left = rect.right + 12;
    if (left + width > window.innerWidth - 12) {
        left = Math.max(12, rect.left - width - 12);
    }
    const top = Math.max(12, Math.min(rect.top, window.innerHeight - height - 12));
    imageListPreview.style.left = left + "px";
    imageListPreview.style.top = top + "px";
}

function showImageListPreview(event) {
    const link = event.target.closest(".image-list-thumbnail");
    if (!link || link === imageListPreviewLink) {
        return;
    }
    if (!imageListPreview) {
        imageListPreview = document.createElement("div");
        imageListPreview.className = "image-list-preview";
        imageListPreview.setAttribute("aria-hidden", "true");
        const image = document.createElement("img");
        image.alt = "";
        image.addEventListener("load", positionImageListPreview);
        image.addEventListener("error", hideImageListPreview);
        imageListPreview.appendChild(image);
        document.body.appendChild(imageListPreview);
    }
    imageListPreviewLink = link;
    imageListPreview.hidden = false;
    imageListPreview.firstElementChild.src = link.dataset.previewUrl;
    positionImageListPreview();
}

function leaveImageListPreview(event) {
    if (imageListPreviewLink && !imageListPreviewLink.contains(event.relatedTarget)) {
        hideImageListPreview();
    }
}

function dismissImageListPreview(event) {
    if (event.key === "Escape") {
        hideImageListPreview();
    }
}

document.addEventListener("mouseover", showImageListPreview);
document.addEventListener("focusin", showImageListPreview);
document.addEventListener("mouseout", leaveImageListPreview);
document.addEventListener("focusout", leaveImageListPreview);
document.addEventListener("keydown", dismissImageListPreview);
document.addEventListener("scroll", hideImageListPreview, true);
window.addEventListener("resize", hideImageListPreview);
