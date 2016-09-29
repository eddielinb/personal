/*
 *  Shared form functions
 *
 */

IMT.time = (function () {
    var date_format = "Y-MM-DD HH:mm:ss";
    var dtp_settings =
        {
            locale: 'en-gb',
            format: date_format,
        };
    function update_dt() {
        var a_date = moment.utc($('#ts').val(), 'X');
        $('#dt').val(a_date.format(date_format));
        var start_date = moment.utc($('#sts').val(), 'X');
        $('#sdt').val(start_date.format(date_format));
        var end_date = moment.utc($('#ets').val(), 'X');
        $('#edt').val(end_date.format(date_format));
    }

    function update_ts() {
        var a_date = moment.utc($('#dt').val(), date_format);
        $('#ts').val(a_date.format('X'));
        var start_date = moment.utc($('#sdt').val(), date_format);
        $('#sts').val(start_date.format('X'));
        var end_date = moment.utc($('#edt').val(), date_format);
        $('#ets').val(end_date.format('X'));
    }
    return {
        date_format: date_format,
        dtp_settings: dtp_settings,
        update_dt: update_dt,
        update_ts: update_ts,
    };
}());

IMT.form = (function () {
    function form_submit_trigger() {
        var clkBtn;
        // click events trigger
        $('button[type="submit"]').click(function(evt) {
            clkBtn = evt.target;
        });
        $('.graph_form').submit(function(e){
            IMT.log($(this), ["form"]);
            if (clkBtn.getAttribute('value') != "json") {
                e.preventDefault();
                IMT.graph.post_data($(this), { name: "data_type", value: clkBtn.getAttribute('value') }, django_post_url, ajax_success_callback, IMT.graph.ajax_error_callback);
            }
        });
    }
    return {
        submit_trigger: form_submit_trigger,
    };
}());

$( document ).ready(function() {

    $('.fetch.cancel').click(function(e){
        var charts = Highcharts.charts;
        $.each(charts, function(chart_index, chart) {
            chart.hideLoading();
        });
        $('.fetch').fadeToggle();
        IMT.xhr.abort();
    });

    $('.ts').change(function(e) {
        IMT.time.update_dt();
    });
    $('.dtpicker').on("dp.change", function(e) {
        IMT.time.update_ts();
    });

    IMT.time.update_dt();

    IMT.form.submit_trigger();

});
