(function () {
    "use strict";

    let viewer = null;
    let viewerPromise = null;
    let dependencyPromise = null;

    function loadScript(url, isReady) {
        if (isReady()) {
            return Promise.resolve();
        }

        return new Promise(function (resolve, reject) {
            const script = document.createElement("script");
            script.src = url;
            script.addEventListener("load", function () {
                if (isReady()) {
                    resolve();
                } else {
                    reject(new Error("Viewer dependency did not initialize: " + url));
                }
            }, { once: true });
            script.addEventListener("error", function () {
                reject(new Error("Could not load viewer dependency: " + url));
            }, { once: true });
            document.head.appendChild(script);
        });
    }

    function loadViewerDependencies(wrapper) {
        if (!dependencyPromise) {
            dependencyPromise = loadScript(
                wrapper.dataset.openseadragonUrl,
                function () { return typeof window.OpenSeadragon === "function"; }
            ).then(function () {
                return loadScript(
                    wrapper.dataset.divaUrl,
                    function () { return typeof window.Diva === "function"; }
                );
            }).catch(function (error) {
                dependencyPromise = null;
                throw error;
            });
        }

        return dependencyPromise;
    }

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

    // async function finishInitialization(instance, wrapper, initialPage) {
    //     await instance.ready;
    //     await goToTarget(instance, initialPage);
    // }

    function initializeViewer() {
        if (viewer) {
            void goToTarget(viewer, pageTargetFromHash());
            return;
        }

        if (viewerPromise) {
            return;
        }

        const wrapper = document.getElementById("diva-wrapper");
        if (!wrapper || !wrapper.dataset.manifestUrl) {
            return;
        }

        viewerPromise = loadViewerDependencies(wrapper).then(function () {
            const initialPage = pageTargetFromHash();
            viewer = new Diva("diva-wrapper", {
                objectData: wrapper.dataset.manifestUrl,
                sidebarPanel: "contents",
                showSidebar: true,
                sidebarWidth: 480,
                showTitle: false,
                initialPage: initialPage
            });
            return viewer;
        }).catch(function (error) {
            viewerPromise = null;
            console.error("Could not initialize the image viewer.", error);
        });

        // These remain compatibility fallbacks until the options are in the npm build.
        // void finishInitialization(viewer, wrapper, initialPage);
    }

    document.addEventListener("initialize-diva", initializeViewer);
    window.addEventListener("hashchange", function () {
        if (viewer) {
            void goToTarget(viewer, pageTargetFromHash());
        }
    });
}());
