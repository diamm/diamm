/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/build/plugins/";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./source/js/plugins/download.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./source/js/plugins/download.js":
/*!***************************************!*\
  !*** ./source/js/plugins/download.js ***!
  \***************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return DownloadPlugin; });\n/**\n * A simple plugin that implements a download button for individual images. Plugins\n * should register themselves as a class in the global Diva namespace, e.g., global.Diva.DownloadPlugin.\n * Plugins are then included as *uninstantiated* references within a plugin configuration. To enable them, simply include\n * plugins: [Diva.DownloadPlugin] when creating a Diva instance.\n * When the viewer is instantiated it will also instantiate the plugin, which\n * will then configure itself.\n *\n * Plugin constructors should take one argument, which is an instance of a ViewerCore object.\n *\n *\n * Plugins should implement the following interface:\n *\n * {boolean} isPageTool - Added to the class prototype. Whether the plugin icon should be included for each page as a page tool\n * {string} pluginName - Added to the class prototype. Defines the name for the plugin.\n *\n * @method createIcon - A div representing the icon. This *should* be implemented using SVG.\n * @method handleClick - The click handler for the icon.\n *\n *\n **/\nclass DownloadPlugin\n{\n    constructor (core)\n    {\n        this.core = core;\n        this.pageToolsIcon = this.createIcon();\n    }\n\n    /**\n    * Open a new window with the page image.\n    *\n    **/\n    handleClick (event, settings, publicInstance, pageIndex)\n    {\n        let width = publicInstance.getPageDimensions(pageIndex).width;\n        let url = publicInstance.getPageImageURL(pageIndex, { width: width });\n        window.open(url);\n    }\n\n    createIcon ()\n    {\n        /*\n        * See img/download.svg for the standalone source code for this.\n        * */\n\n        const pageToolsIcon = document.createElement('div');\n        pageToolsIcon.classList.add('diva-download-icon');\n\n        let root = document.createElementNS(\"http://www.w3.org/2000/svg\", \"svg\");\n        root.setAttribute(\"x\", \"0px\");\n        root.setAttribute(\"y\", \"0px\");\n        root.setAttribute(\"viewBox\", \"0 0 25 25\");\n        root.id = `${this.core.settings.selector}download-icon`;\n\n        let g = document.createElementNS(\"http://www.w3.org/2000/svg\", \"g\");\n        g.id = `${this.core.settings.selector}download-icon-glyph`;\n        g.setAttribute(\"transform\", \"matrix(1, 0, 0, 1, -11.5, -11.5)\");\n        g.setAttribute(\"class\", \"diva-pagetool-icon\");\n\n        let path = document.createElementNS(\"http://www.w3.org/2000/svg\", \"path\");\n        path.setAttribute(\"d\", \"M36.25,24c0,6.755-5.495,12.25-12.25,12.25S11.75,30.755,11.75,24S17.245,11.75,24,11.75S36.25,17.245,36.25,24z M33,24c0-4.963-4.037-9-9-9s-9,4.037-9,9s4.037,9,9,9S33,28.963,33,24z M29.823,23.414l-5.647,7.428c-0.118,0.152-0.311,0.117-0.428-0.035L18.1,23.433C17.982,23.28,18.043,23,18.235,23H21v-4.469c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5V23h2.688C29.879,23,29.941,23.263,29.823,23.414z\");\n\n        g.appendChild(path);\n        root.appendChild(g);\n\n        pageToolsIcon.appendChild(root);\n\n        return pageToolsIcon;\n    }\n}\n\nDownloadPlugin.prototype.pluginName = \"download\";\nDownloadPlugin.prototype.isPageTool = true;\n\n/**\n * Make this plugin available in the global context\n * as part of the 'Diva' namespace.\n **/\n(function (global)\n{\n    global.Diva.DownloadPlugin = DownloadPlugin;\n})(window);\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zb3VyY2UvanMvcGx1Z2lucy9kb3dubG9hZC5qcy5qcyIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL3NvdXJjZS9qcy9wbHVnaW5zL2Rvd25sb2FkLmpzP2FiYzgiXSwic291cmNlc0NvbnRlbnQiOlsiLyoqXG4gKiBBIHNpbXBsZSBwbHVnaW4gdGhhdCBpbXBsZW1lbnRzIGEgZG93bmxvYWQgYnV0dG9uIGZvciBpbmRpdmlkdWFsIGltYWdlcy4gUGx1Z2luc1xuICogc2hvdWxkIHJlZ2lzdGVyIHRoZW1zZWx2ZXMgYXMgYSBjbGFzcyBpbiB0aGUgZ2xvYmFsIERpdmEgbmFtZXNwYWNlLCBlLmcuLCBnbG9iYWwuRGl2YS5Eb3dubG9hZFBsdWdpbi5cbiAqIFBsdWdpbnMgYXJlIHRoZW4gaW5jbHVkZWQgYXMgKnVuaW5zdGFudGlhdGVkKiByZWZlcmVuY2VzIHdpdGhpbiBhIHBsdWdpbiBjb25maWd1cmF0aW9uLiBUbyBlbmFibGUgdGhlbSwgc2ltcGx5IGluY2x1ZGVcbiAqIHBsdWdpbnM6IFtEaXZhLkRvd25sb2FkUGx1Z2luXSB3aGVuIGNyZWF0aW5nIGEgRGl2YSBpbnN0YW5jZS5cbiAqIFdoZW4gdGhlIHZpZXdlciBpcyBpbnN0YW50aWF0ZWQgaXQgd2lsbCBhbHNvIGluc3RhbnRpYXRlIHRoZSBwbHVnaW4sIHdoaWNoXG4gKiB3aWxsIHRoZW4gY29uZmlndXJlIGl0c2VsZi5cbiAqXG4gKiBQbHVnaW4gY29uc3RydWN0b3JzIHNob3VsZCB0YWtlIG9uZSBhcmd1bWVudCwgd2hpY2ggaXMgYW4gaW5zdGFuY2Ugb2YgYSBWaWV3ZXJDb3JlIG9iamVjdC5cbiAqXG4gKlxuICogUGx1Z2lucyBzaG91bGQgaW1wbGVtZW50IHRoZSBmb2xsb3dpbmcgaW50ZXJmYWNlOlxuICpcbiAqIHtib29sZWFufSBpc1BhZ2VUb29sIC0gQWRkZWQgdG8gdGhlIGNsYXNzIHByb3RvdHlwZS4gV2hldGhlciB0aGUgcGx1Z2luIGljb24gc2hvdWxkIGJlIGluY2x1ZGVkIGZvciBlYWNoIHBhZ2UgYXMgYSBwYWdlIHRvb2xcbiAqIHtzdHJpbmd9IHBsdWdpbk5hbWUgLSBBZGRlZCB0byB0aGUgY2xhc3MgcHJvdG90eXBlLiBEZWZpbmVzIHRoZSBuYW1lIGZvciB0aGUgcGx1Z2luLlxuICpcbiAqIEBtZXRob2QgY3JlYXRlSWNvbiAtIEEgZGl2IHJlcHJlc2VudGluZyB0aGUgaWNvbi4gVGhpcyAqc2hvdWxkKiBiZSBpbXBsZW1lbnRlZCB1c2luZyBTVkcuXG4gKiBAbWV0aG9kIGhhbmRsZUNsaWNrIC0gVGhlIGNsaWNrIGhhbmRsZXIgZm9yIHRoZSBpY29uLlxuICpcbiAqXG4gKiovXG5leHBvcnQgZGVmYXVsdCBjbGFzcyBEb3dubG9hZFBsdWdpblxue1xuICAgIGNvbnN0cnVjdG9yIChjb3JlKVxuICAgIHtcbiAgICAgICAgdGhpcy5jb3JlID0gY29yZTtcbiAgICAgICAgdGhpcy5wYWdlVG9vbHNJY29uID0gdGhpcy5jcmVhdGVJY29uKCk7XG4gICAgfVxuXG4gICAgLyoqXG4gICAgKiBPcGVuIGEgbmV3IHdpbmRvdyB3aXRoIHRoZSBwYWdlIGltYWdlLlxuICAgICpcbiAgICAqKi9cbiAgICBoYW5kbGVDbGljayAoZXZlbnQsIHNldHRpbmdzLCBwdWJsaWNJbnN0YW5jZSwgcGFnZUluZGV4KVxuICAgIHtcbiAgICAgICAgbGV0IHdpZHRoID0gcHVibGljSW5zdGFuY2UuZ2V0UGFnZURpbWVuc2lvbnMocGFnZUluZGV4KS53aWR0aDtcbiAgICAgICAgbGV0IHVybCA9IHB1YmxpY0luc3RhbmNlLmdldFBhZ2VJbWFnZVVSTChwYWdlSW5kZXgsIHsgd2lkdGg6IHdpZHRoIH0pO1xuICAgICAgICB3aW5kb3cub3Blbih1cmwpO1xuICAgIH1cblxuICAgIGNyZWF0ZUljb24gKClcbiAgICB7XG4gICAgICAgIC8qXG4gICAgICAgICogU2VlIGltZy9kb3dubG9hZC5zdmcgZm9yIHRoZSBzdGFuZGFsb25lIHNvdXJjZSBjb2RlIGZvciB0aGlzLlxuICAgICAgICAqICovXG5cbiAgICAgICAgY29uc3QgcGFnZVRvb2xzSWNvbiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO1xuICAgICAgICBwYWdlVG9vbHNJY29uLmNsYXNzTGlzdC5hZGQoJ2RpdmEtZG93bmxvYWQtaWNvbicpO1xuXG4gICAgICAgIGxldCByb290ID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudE5TKFwiaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmdcIiwgXCJzdmdcIik7XG4gICAgICAgIHJvb3Quc2V0QXR0cmlidXRlKFwieFwiLCBcIjBweFwiKTtcbiAgICAgICAgcm9vdC5zZXRBdHRyaWJ1dGUoXCJ5XCIsIFwiMHB4XCIpO1xuICAgICAgICByb290LnNldEF0dHJpYnV0ZShcInZpZXdCb3hcIiwgXCIwIDAgMjUgMjVcIik7XG4gICAgICAgIHJvb3QuaWQgPSBgJHt0aGlzLmNvcmUuc2V0dGluZ3Muc2VsZWN0b3J9ZG93bmxvYWQtaWNvbmA7XG5cbiAgICAgICAgbGV0IGcgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50TlMoXCJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Z1wiLCBcImdcIik7XG4gICAgICAgIGcuaWQgPSBgJHt0aGlzLmNvcmUuc2V0dGluZ3Muc2VsZWN0b3J9ZG93bmxvYWQtaWNvbi1nbHlwaGA7XG4gICAgICAgIGcuc2V0QXR0cmlidXRlKFwidHJhbnNmb3JtXCIsIFwibWF0cml4KDEsIDAsIDAsIDEsIC0xMS41LCAtMTEuNSlcIik7XG4gICAgICAgIGcuc2V0QXR0cmlidXRlKFwiY2xhc3NcIiwgXCJkaXZhLXBhZ2V0b29sLWljb25cIik7XG5cbiAgICAgICAgbGV0IHBhdGggPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50TlMoXCJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Z1wiLCBcInBhdGhcIik7XG4gICAgICAgIHBhdGguc2V0QXR0cmlidXRlKFwiZFwiLCBcIk0zNi4yNSwyNGMwLDYuNzU1LTUuNDk1LDEyLjI1LTEyLjI1LDEyLjI1UzExLjc1LDMwLjc1NSwxMS43NSwyNFMxNy4yNDUsMTEuNzUsMjQsMTEuNzVTMzYuMjUsMTcuMjQ1LDM2LjI1LDI0eiBNMzMsMjRjMC00Ljk2My00LjAzNy05LTktOXMtOSw0LjAzNy05LDlzNC4wMzcsOSw5LDlTMzMsMjguOTYzLDMzLDI0eiBNMjkuODIzLDIzLjQxNGwtNS42NDcsNy40MjhjLTAuMTE4LDAuMTUyLTAuMzExLDAuMTE3LTAuNDI4LTAuMDM1TDE4LjEsMjMuNDMzQzE3Ljk4MiwyMy4yOCwxOC4wNDMsMjMsMTguMjM1LDIzSDIxdi00LjQ2OWMwLTAuMjc1LDAuMjI1LTAuNSwwLjUtMC41aDVjMC4yNzUsMCwwLjUsMC4yMjUsMC41LDAuNVYyM2gyLjY4OEMyOS44NzksMjMsMjkuOTQxLDIzLjI2MywyOS44MjMsMjMuNDE0elwiKTtcblxuICAgICAgICBnLmFwcGVuZENoaWxkKHBhdGgpO1xuICAgICAgICByb290LmFwcGVuZENoaWxkKGcpO1xuXG4gICAgICAgIHBhZ2VUb29sc0ljb24uYXBwZW5kQ2hpbGQocm9vdCk7XG5cbiAgICAgICAgcmV0dXJuIHBhZ2VUb29sc0ljb247XG4gICAgfVxufVxuXG5Eb3dubG9hZFBsdWdpbi5wcm90b3R5cGUucGx1Z2luTmFtZSA9IFwiZG93bmxvYWRcIjtcbkRvd25sb2FkUGx1Z2luLnByb3RvdHlwZS5pc1BhZ2VUb29sID0gdHJ1ZTtcblxuLyoqXG4gKiBNYWtlIHRoaXMgcGx1Z2luIGF2YWlsYWJsZSBpbiB0aGUgZ2xvYmFsIGNvbnRleHRcbiAqIGFzIHBhcnQgb2YgdGhlICdEaXZhJyBuYW1lc3BhY2UuXG4gKiovXG4oZnVuY3Rpb24gKGdsb2JhbClcbntcbiAgICBnbG9iYWwuRGl2YS5Eb3dubG9hZFBsdWdpbiA9IERvd25sb2FkUGx1Z2luO1xufSkod2luZG93KTtcbiJdLCJtYXBwaW5ncyI6IkFBQUE7QUFBQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Iiwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./source/js/plugins/download.js\n");

/***/ })

/******/ });