const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { test } = require("node:test");
const vm = require("node:vm");

const script = readFileSync("diamm/static/admin/image-thumbnails.js", "utf8");

function setup() {
    const listeners = {};
    const elements = [];
    const body = [];
    const window = {
        innerWidth: 1000,
        innerHeight: 800,
        addEventListener(name, callback) { listeners[name] = callback; }
    };
    const document = {
        body: { appendChild(element) { body.push(element); } },
        addEventListener(name, callback) { listeners[name] = callback; },
        createElement(tag) {
            const element = {
                tag,
                hidden: false,
                style: {},
                offsetWidth: 360,
                offsetHeight: 480,
                listeners: {},
                setAttribute(name, value) { this[name] = value; },
                addEventListener(name, callback) { this.listeners[name] = callback; },
                appendChild(child) { this.firstElementChild = child; }
            };
            elements.push(element);
            return element;
        }
    };
    vm.runInNewContext(script, { window, document });
    return { listeners, elements, body };
}

function thumbnail(url = "/admin/image/1/preview/large/") {
    const link = {
        dataset: { previewUrl: url },
        contains(target) { return target === this || target === this.image; },
        getBoundingClientRect() { return { top: 100, left: 100, right: 164 }; }
    };
    link.image = { closest() { return link; } };
    return link;
}

test("large preview is created and loaded only on hover", () => {
    const app = setup();
    const link = thumbnail();
    assert.equal(app.elements.length, 0);
    app.listeners.mouseover({ target: link.image });
    assert.equal(app.body.length, 1);
    assert.equal(app.body[0].firstElementChild.src, link.dataset.previewUrl);
    assert.equal(app.body[0].hidden, false);
    assert.equal(app.body[0].style.left, "176px");
    app.listeners.mouseover({ target: link.image });
    assert.equal(app.body.length, 1);
});

test("moving inside the thumbnail keeps it open and leaving hides it", () => {
    const app = setup();
    const link = thumbnail();
    app.listeners.mouseover({ target: link.image });
    app.listeners.mouseout({ relatedTarget: link.image });
    assert.equal(app.body[0].hidden, false);
    app.listeners.mouseout({ relatedTarget: null });
    assert.equal(app.body[0].hidden, true);
});

test("keyboard focus shows the preview and Escape dismisses it", () => {
    const app = setup();
    const link = thumbnail();
    app.listeners.focusin({ target: link.image });
    assert.equal(app.body[0].hidden, false);
    app.listeners.keydown({ key: "Escape" });
    assert.equal(app.body[0].hidden, true);
    app.listeners.focusin({ target: link.image });
    app.listeners.focusout({ relatedTarget: null });
    assert.equal(app.body[0].hidden, true);
});

test("preview switches images and stays within the viewport", () => {
    const app = setup();
    const first = thumbnail();
    const second = thumbnail("/admin/image/2/preview/large/");
    second.getBoundingClientRect = () => ({ top: 750, left: 900, right: 964 });
    app.listeners.mouseover({ target: first.image });
    app.listeners.mouseover({ target: second.image });
    assert.equal(app.body.length, 1);
    assert.equal(app.body[0].firstElementChild.src, second.dataset.previewUrl);
    assert.equal(app.body[0].style.left, "528px");
    assert.equal(app.body[0].style.top, "308px");
    app.body[0].firstElementChild.listeners.error();
    assert.equal(app.body[0].hidden, true);
});

test("scroll and resize hide a stale preview", () => {
    const app = setup();
    const link = thumbnail();
    app.listeners.mouseover({ target: link.image });
    app.listeners.scroll();
    assert.equal(app.body[0].hidden, true);
    app.listeners.mouseover({ target: link.image });
    app.listeners.resize();
    assert.equal(app.body[0].hidden, true);
});

test("preview width is at least 300px on desktop", () => {
    const css = readFileSync("diamm/static/admin/image-thumbnails.css", "utf8");
    assert.match(css, /\.image-list-preview\s*\{[^}]*width:\s*360px/);
});
