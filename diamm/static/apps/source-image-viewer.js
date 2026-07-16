(function () {
    "use strict";

    let viewer = null;

    function pageTargetFromHash() {
        const queryStart = window.location.hash.indexOf("?");
        if (queryStart === -1) {
            return null;
        }
        return new URLSearchParams(window.location.hash.slice(queryStart + 1)).get("p");
    }

    function pageIndexForTarget(instance, target) {
        if (!target) {
            return null;
        }

        const pages = instance.getPages();
        if (target.startsWith("canvas:")) {
            const canvasId = target.slice("canvas:".length);
            const page = pages.find(candidate => candidate.canvasId === canvasId);
            return page ? page.index : null;
        }

        // Diva 6 accepted an unprefixed folio label. Keep those bookmarks working.
        const normalized = target.toLocaleLowerCase();
        const exact = pages.find(candidate => candidate.label.toLocaleLowerCase() === normalized);
        const page = exact || pages.find(candidate => candidate.label.toLocaleLowerCase().includes(normalized));
        return page ? page.index : null;
    }

    async function goToTarget(instance, target) {
        if (!target) {
            return;
        }
        await instance.ready;
        const pageIndex = pageIndexForTarget(instance, target);
        if (pageIndex === null || instance.getState().currentPageIndex === pageIndex) {
            return;
        }
        await instance.goToPage(pageIndex);
    }

    async function finishInitialization(instance, wrapper, initialPage) {
        await instance.ready;

        // The pre-release 7.4 build accepts sidebarPanel as a forward-compatible
        // option but does not act on it yet. Open Contents until the npm build does.
        const contentsButton = Array.from(
            wrapper.querySelectorAll("button.sidebar-tab-button")
        ).find(button => button.textContent.trim() === "Contents");
        if (contentsButton) {
            contentsButton.click();
        }

        await goToTarget(instance, initialPage);
    }

    function initializeViewer() {
        if (viewer) {
            void goToTarget(viewer, pageTargetFromHash());
            return;
        }

        const wrapper = document.getElementById("diva-wrapper");
        if (!wrapper || !wrapper.dataset.manifestUrl) {
            return;
        }

        const initialPage = pageTargetFromHash();
        viewer = new Diva("diva-wrapper", {
            objectData: wrapper.dataset.manifestUrl,
            sidebarPanel: "contents",
            showSidebar: true,
            showTitle: false,
            initialPage: initialPage
        });

        // These remain compatibility fallbacks until the options are in the npm build.
        void finishInitialization(viewer, wrapper, initialPage);
    }

    document.addEventListener("initialize-diva", initializeViewer);
    window.addEventListener("hashchange", function () {
        if (viewer) {
            void goToTarget(viewer, pageTargetFromHash());
        }
    });
}());
