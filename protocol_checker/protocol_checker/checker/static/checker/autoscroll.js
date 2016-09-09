// var top, left;

window.onbeforeunload = function() {
    var top  = window.pageYOffset || document.documentElement.scrollTop,
        left = window.pageXOffset || document.documentElement.scrollLeft;
    sessionStorage.setItem('top', top);
    sessionStorage.setItem('left', left);
};

window.onload = function() {
    var top = sessionStorage.getItem('top');
    var left = sessionStorage.getItem('left');
    if ((top !== null) && (left !== null)) {
        window.scroll(parseInt(left), parseInt(top));
        // console.log(top);
    }
};

$(document).ready(function () {
});
