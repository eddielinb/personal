window.onbeforeunload = function() {
    sessionStorage.setItem('mac', $('#id_mac').val());
    sessionStorage.setItem('config', $('#id_config').val());
    sessionStorage.setItem('auto', $('div #autoreload-button').hasClass("btn-primary"));
};

window.onload = function() {
    var mac = sessionStorage.getItem('mac');
    var config = sessionStorage.getItem('config');
    var auto = sessionStorage.getItem('auto');
    if (mac !== null) $('#id_mac').val(mac);
    if (config !== null) $('#id_config').val(config);
    if (auto !== null)
        if (!auto)
            $(this).toggleClass("btn-primary btn-outline-primary");
};

$('div #autoreload-button').click(function() {
    $(this).toggleClass("btn-primary btn-outline-primary");
});

function refresh() {
    if ($('div #autoreload-button').hasClass("btn-primary"))
        window.location.reload(true);
    else {
        setTimeout(refresh, 8000);
    }
}

$(document).ready(function () {
    setTimeout(refresh, 8000);
});
