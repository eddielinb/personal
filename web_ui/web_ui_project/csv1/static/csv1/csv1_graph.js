/*
 *  CSV
 *
 */

IMT.chart_settings = (function () {

    var chart_settings = [
        $.extend(true, {}, IMT.graph.options.power, IMT.graph.options.v1),
        $.extend(true, {}, IMT.graph.options.power, IMT.graph.options.v2),
        $.extend(true, {}, IMT.graph.options.power, IMT.graph.options.v3),
    ];

    return chart_settings;

}());

function get_data(wave_data, chart) {
    var series=[];
    var colourPalette = ["#007298", "#65cce9", "#f56e00", "#5e4565", "#a5a5a5", "#00ae79", "#0a2f5d", "#ffbd06",'#058DC7'];
    if (chart.options.chart.renderTo == 'graph1') {
        data = wave_data.data;
        time_data = data.timestamps;
        time_data = time_data.map(function(x) { return x * 1000; });
        power_data = data.root_powers;
        series.push({
            name: "Aggregate",
            data: IMT.zip(time_data,power_data),
            colour: colourPalette[series.length%8]
        });
    } else if (chart.options.chart.renderTo == 'graph2') {
        data = wave_data.data;
        time_data = data.timestamps;
        time_data = time_data.map(function(x) { return x * 1000; });
        power_data = data.root_powers;
        series.push({
            name: "Aggregate",
            data: IMT.zip(time_data,power_data),
        });
        $.each(data.apps, function(type_index, app) {
            series.push({
                name: app.app_type_name + ":" + app.app_id,
                data: IMT.zip(time_data,app.app_powers),
                colour: colourPalette[series.length%8]
            });
        });
    } else if (chart.options.chart.renderTo == 'graph3') {
        data = wave_data.data;
        time_data = data.timestamps;
        time_data = time_data.map(function(x) { return x * 1000; });
        $.each(data.apps, function(type_index, app) {
            series.push({
                name: app.app_type_name + ":" + app.app_id,
                data: IMT.zip(time_data,app.app_powers),
                colour: colourPalette[(series.length+1)%8]
            });
        });
    }
    return {
        series_list: series,
    };
}

function ajax_success_callback(new_data){
    IMT.json_data=new_data;
    IMT.log(new_data, ["ajax", "callback"]);

    $('.fetch').fadeToggle();
    populate_table(IMT.json_data);

    var charts = Highcharts.charts;
    $.each(charts, function(chart_index, chart) {
        if (!('wave_data' in IMT.json_data)) {
            chart.showLoading("Error");
        } else if ('error' in IMT.json_data.wave_data) {
            chart.showLoading(IMT.json_data.wave_data['error']);
        } else {
            IMT.graph.load_chart($('.graph-div').eq(chart_index), true);
        }
        chart.zoom();
    });
}

function populate_table(json_data) {
    document.getElementById('get_data').innerHTML = json_data.headers.data_type;
    document.getElementById('get_service').innerHTML = json_data.headers.service_id;
    document.getElementById('get_user').innerHTML = json_data.headers.user_id;
    document.getElementById('get_ts').innerHTML = json_data.headers.ts;
    document.getElementById('get_tz').innerHTML = json_data.headers.tz;

    var str = json_data.headers.data_type;
    document.getElementById('data-heading').innerHTML = "CSV " + str.replace("_", " ");
}

///////////////////////////////////////////////////////////////////////////////

$( document ).ready(function() {

    $('#dtpicker').datetimepicker(IMT.time.dtp_settings);

    IMT.graph.instantiate_charts(IMT.chart_settings);

    IMT.graph.post_data(
        $('.graph_form'),
        { name: "data_type",
        value: django_populate_values_data_type },
        django_post_url,
        ajax_success_callback,
        IMT.graph.ajax_error_callback
    );

});
