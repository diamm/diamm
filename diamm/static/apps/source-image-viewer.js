(function () {
    "use strict";

    let viewer = null;
    let viewerPromise = null;
    let dependencyPromise = null;
    let viewerGeneration = 0;

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

    function initialPageForTarget(target) {
        if (!target) {
            return undefined;
        }

        if (target.startsWith("canvas:")) {
            const canvasId = target.slice("canvas:".length);
            return canvasId ? { by: "canvasId", value: canvasId } : undefined;
        }

        return { by: "label", value: target };
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

    function initializeViewer(useHashTarget = true) {
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

        const generation = viewerGeneration;
        viewerPromise = loadViewerDependencies(wrapper).then(function () {
            if (generation !== viewerGeneration) {
                return;
            }
            const initialTarget = useHashTarget ? pageTargetFromHash() : null;
            viewer = new Diva("diva-wrapper", {
                objectData: wrapper.dataset.manifestUrl,
                sidebarPanel: "contents",
                showSidebar: true,
                sidebarWidth: 480,
                showTitle: false,
                showLogoutButton: false,
                initialPage: initialPageForTarget(initialTarget)
            });
            return goToTarget(viewer, initialTarget).then(function () {
                return viewer;
            });
        }).catch(function (error) {
            if (generation !== viewerGeneration) {
                return;
            }
            viewerPromise = null;
            console.error("Could not initialize the image viewer.", error);
        });
    }

    document.addEventListener("initialize-diva", function () {
        initializeViewer();
    });
    document.addEventListener("change", function (event) {
        if (event.target.id !== "manifest-selector") {
            return;
        }

        const wrapper = document.getElementById("diva-wrapper");
        if (!wrapper || wrapper.dataset.manifestUrl === event.target.value) {
            return;
        }

        viewerGeneration += 1;
        if (viewer) {
            viewer.destroy();
            viewer = null;
        }
        viewerPromise = null;
        wrapper.replaceChildren();
        wrapper.dataset.manifestUrl = event.target.value;

        // A page bookmark from the old manifest does not apply to the new one.
        window.history.replaceState(null, "", "#/images");
        initializeViewer(false);
    });
    window.addEventListener("hashchange", function () {
        if (viewer) {
            void goToTarget(viewer, pageTargetFromHash());
        }
    });
}());
