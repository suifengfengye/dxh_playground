/**
 * Webpack Bundle Analysis - Formatted Version
 * This is a formatted version of the minified webpack bundle
 * to help understand the structure and functionality
 */

(() => {
    "use strict";

    // Webpack runtime and module system
    var modules = {
        // CSS Loader module
        291: function(module) {
            module.exports = function(css) {
                return css[1];
            };
        },

        // CSS Processing module
        534: function(module, exports, require) {
            var cssLoader = require(291);
            var cssLoaderExport = require.n(cssLoader);
            var cssContent = require(748);
            
            // Process and inject CSS
            require.n(cssContent)()(cssLoaderExport()).push([
                module.id,
                `.div {
    color: red;
    font-size: 20px;
}`,
                ""
            ]);
        },

        // CSS Content module
        748: function(module) {
            module.exports = function(css) {
                var list = [];
                
                list.toString = function() {
                    return this.map(function(item) {
                        var content = "";
                        var hasLayer = void 0 !== item[5];
                        
                        if (item[4]) {
                            content += "@supports (".concat(item[4], ") {");
                        }
                        if (item[2]) {
                            content += "@media ".concat(item[2], " {");
                        }
                        if (hasLayer) {
                            content += "@layer".concat(
                                item[5].length > 0 ? " ".concat(item[5]) : "", 
                                " {"
                            );
                        }
                        
                        content += css(item);
                        
                        if (hasLayer) content += "}";
                        if (item[2]) content += "}";
                        if (item[4]) content += "}";
                        
                        return content;
                    }).join("");
                };
                
                list.i = function(css, media, dedupe, supports, layer) {
                    if (typeof css === "string") {
                        css = [[null, css, void 0]];
                    }
                    
                    var alreadyImportedModules = {};
                    
                    if (dedupe) {
                        for (var i = 0; i < this.length; i++) {
                            var id = this[i][0];
                            if (id != null) {
                                alreadyImportedModules[id] = true;
                            }
                        }
                    }
                    
                    for (var j = 0; j < css.length; j++) {
                        var item = [].concat(css[j]);
                        
                        if (dedupe && alreadyImportedModules[item[0]]) {
                            continue;
                        }
                        
                        if (layer) {
                            if (!item[5]) {
                                item[1] = "@layer".concat(
                                    item[5].length > 0 ? " ".concat(item[5]) : "", 
                                    " {"
                                ).concat(item[1], "}");
                            }
                            item[5] = layer;
                        }
                        
                        if (media) {
                            if (!item[2]) {
                                item[2] = media;
                            } else {
                                item[1] = "@media ".concat(item[2], " {").concat(item[1], "}");
                                item[2] = media;
                            }
                        }
                        
                        if (supports) {
                            if (!item[4]) {
                                item[4] = "".concat(supports);
                            } else {
                                item[1] = "@supports (".concat(item[4], ") {").concat(item[1], "}");
                                item[4] = supports;
                            }
                        }
                        
                        list.push(item);
                    }
                };
                
                return list;
            };
        }
    };

    // Webpack require function and module cache
    var moduleCache = {};

    function require(moduleId) {
        var cachedModule = moduleCache[moduleId];
        if (void 0 !== cachedModule) {
            return cachedModule.exports;
        }
        
        var module = moduleCache[moduleId] = {
            id: moduleId,
            exports: {}
        };
        
        modules[moduleId](module, module.exports, require);
        return module.exports;
    }

    // Webpack helper functions
    require.n = function(module) {
        var getter = module && module.__esModule 
            ? function() { return module.default; } 
            : function() { return module; };
        
        require.d(getter, { a: getter });
        return getter;
    };

    require.d = function(exports, definition) {
        for (var key in definition) {
            if (require.o(definition, key) && !require.o(exports, key)) {
                Object.defineProperty(exports, key, {
                    enumerable: true,
                    get: definition[key]
                });
            }
        }
    };

    require.o = function(object, property) {
        return Object.prototype.hasOwnProperty.call(object, property);
    };

    // Load the CSS processing module
    require(534);

    // Application code - Create and style a div element
    const divElement = document.createElement("div");
    divElement.classList.add("div");
    divElement.textContent = "Hello World!";
    document.body.appendChild(divElement);

    // Execute the function from our source code
    console.log("hello world");
})();