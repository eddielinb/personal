/*
 *  Shared utility functions
 *  http://www.adequatelygood.com/JavaScript-Module-Pattern-In-Depth.html
 *  https://toddmotto.com/mastering-the-module-pattern/
 */
var IMT = IMT || {};

IMT.logger = (function () {
    var debug = true;
    var log_tags = [];
    var log_label = null;
    function _intersect_safe(a, b) {
        var ai = 0;
        var bi= 0;
        while( ai < a.length && bi < b.length ){
            if      (a[ai] < b[bi] ){ ai++; }
            else if (a[ai] > b[bi] ){ bi++; }
            else /* they're equal */
            {
                return true;
            }
        }
        return false;
    }
    function _print(msg, tags) {
        var tag_str = "";
        if (!(typeof tags === 'undefined')) {
            var length = tags.length;
            for (var i = 0; i < length; i++) {
                tag_str += tags[i];
                tag_str += ", ";
            }
        }
        console.groupCollapsed(tag_str);
        console.log(msg);
        console.groupEnd();
    }
    function _logg(msg, label) {
        if (debug) {
            if (log_label === label) {
                console.log(msg);
            } else {
                if (!(log_label === null)) {
                    console.groupEnd();
                }
                log_label = label;
                console.groupCollapsed(label);
                console.log(msg);
            }
        }
    }
    function _log(msg, tags) {
        if (debug) {
            if (!(log_label === null)) {
                console.groupEnd();
                log_label = null;
            }
            if (typeof tags === 'string' || tags instanceof String) {
                tags = [tags];
            }
            if (typeof tags === 'undefined') {
                console.log(msg);
            } else if (log_tags.length === 0) {
                _print(msg, tags);
            } else if (_intersect_safe(log_tags, tags)) {
                _print(msg, tags);
            }
        }
    }
    return {
        log: _log,
        log_group: _logg,
    };
}());
IMT.log = IMT.logger.log;
IMT.logg = IMT.logger.log_group;

IMT.zip = function() {
    for (var i = 0; i < arguments.length; i++) {
        if (!arguments[i].length || !arguments.toString()) {
            return false;
        }
        if (i >= 1) {
            if (arguments[i].length !== arguments[i - 1].length) {
                return false;
            }
        }
    }
    var zipped = [];
    for (var j = 0; j < arguments[0].length; j++) {
        var toBeZipped = [];
        for (var k = 0; k < arguments.length; k++) {
            toBeZipped.push(arguments[k][j]);
        }
        zipped.push(toBeZipped);
    }
    return zipped;
};

/********************************************************************
 * Random Colours                                                   *
 * TODO: Check if still mkaes light colours                         *
 ********************************************************************/
IMT.colour = (function () {
    function isTooLightYIQ(hex_colour){
        var r = parseInt(hex_colour.substr(0,2),16);
        var g = parseInt(hex_colour.substr(2,2),16);
        var b = parseInt(hex_colour.substr(4,2),16);
        var yiq = ((r*299)+(g*587)+(b*114))/1000;
        return yiq >= 164;  // Configure value
    }
    function randomColour() {
        var hex_colour = ((Math.random() * 0xFFFFFF) << 0).toString(16);
        if (isTooLightYIQ(hex_colour))
            return randomColour();
        else {
            IMT.log('#' + hex_colour, ["colour"]);
            return '#' + hex_colour;
        }
    }
    function randomColours(n) {
        var colours = [];
        for (var i = 0; i < n; i++) {
            colours.push(randomColour());
        }
        return colours;
    }
    return {
        get: randomColour,
        getMany: randomColours,
    };
}());
