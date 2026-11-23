const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { test } = require("node:test");
const vm = require("node:vm");

const script = readFileSync("diamm/static/apps/source-image-viewer.js", "utf8");

function setup() {
    const listeners = {};
    const instances = [];
    const wrapper = {
        dataset: { manifestUrl: "https://example.org/first" },
        replaceChildren() { this.cleared = true; }
    };
    const window = {
        location: { hash: "#/images?p=old-page" },
        history: {
            replaceState(state, title, hash) { window.location.hash = hash; }
        },
        OpenSeadragon() {},
        addEventListener() {}
    };
    function Diva(id, options) {
        this.options = options;
        this.ready = Promise.resolve();
        this.getPages = () => [];
        this.destroy = () => { this.destroyed = true; };
        instances.push(this);
    }
    window.Diva = Diva;
    vm.runInNewContext(script, {
        window, Diva, URLSearchParams, console,
        document: {
            getElementById: () => wrapper,
            addEventListener: (name, callback) => { listeners[name] = callback; }
        }
    });
    return {
        instances, wrapper, window,
        initialize: () => listeners["initialize-diva"](),
        select: value => listeners.change({ target: { id: "manifest-selector", value } })
    };
}

async function flush() {
    for (let i = 0; i < 10; i++) await Promise.resolve();
}

test("switching destroys and clears the old viewer and drops its page target", async () => {
    const app = setup();
    app.initialize();
    await flush();
    assert.equal(app.instances[0].options.objectData, "https://example.org/first");
    app.select("https://example.org/second");
    assert.equal(app.instances[0].destroyed, true);
    assert.equal(app.wrapper.cleared, true);
    await flush();
    assert.equal(app.instances.length, 2);
    assert.equal(app.instances[1].options.objectData, "https://example.org/second");
    assert.equal(app.instances[1].options.initialPage, undefined);
    assert.equal(app.window.location.hash, "#/images");
    app.initialize();
    await flush();
    assert.equal(app.instances.length, 2);
});

test("rapid selections during initialization create only the latest viewer", async () => {
    const app = setup();
    app.initialize();
    app.select("https://example.org/second");
    app.select("https://example.org/third");
    await flush();
    assert.equal(app.instances.length, 1);
    assert.equal(app.instances[0].options.objectData, "https://example.org/third");
});

test("reselecting the active manifest does not recreate the viewer", async () => {
    const app = setup();
    app.initialize();
    await flush();
    app.select("https://example.org/first");
    await flush();
    assert.equal(app.instances.length, 1);
    assert.equal(app.instances[0].destroyed, undefined);
});
