/*
 *  imGate API
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

get_data = (function (wave_data, chart) {

    var app_map = JSON.parse(django_app_map_string);
    var time_map = JSON.parse(django_time_map_string);
    var colourCount;
    var colourPalette = IMT.colour.getMany(colourCount);

    function get_series_data(wave_data, chart) {
        var series=[];
        if (chart.options.chart.renderTo == 'graph1') {
            $.each(wave_data.data, function(zoom_index, data) {
                time_data = data.timestamps;
                time_data = time_data.map(function(x) { return x * 1000; });
                power_data = data.root_powers;
                series.push({
                    name: time_map[data.time_unit_id],
                    data: IMT.zip(time_data,power_data),
                    colour: colourPalette[series.length%colourCount]
                });
            });
        } else if (chart.options.chart.renderTo == 'graph2') {
            data = wave_data.data[0];
            time_data = data.timestamps;
            time_data = time_data.map(function(x) { return x * 1000; });
            power_data = data.root_powers;
            series.push({
                name: "Aggregate",
                data: IMT.zip(time_data,power_data),
            });
            $.each(data.appliance_types, function(type_index, appliance_type_data) {
                $.each(appliance_type_data.appliances, function(appliance_index, appliance_data) {
                    series.push({
                        name: app_map[appliance_type_data.appliance_type_id.toString()].name+" "+appliance_type_data.appliance_type_id + ":" +appliance_data.appliance_id,
                        data: IMT.zip(time_data,appliance_data.powers),
                        colour: colourPalette[series.length%colourCount],
                    });
                });
            });
        } else if (chart.options.chart.renderTo == 'graph3') {
            data = wave_data.data[0];
            time_data = data.timestamps;
            time_data = time_data.map(function(x) { return x * 1000; });
            $.each(data.appliance_types, function(type_index, appliance_type_data) {
                $.each(appliance_type_data.appliances, function(appliance_index, appliance_data) {
                    series.push({
                        name: app_map[appliance_type_data.appliance_type_id.toString()].name+" "+appliance_type_data.appliance_type_id + ":" +appliance_data.appliance_id,
                        data: IMT.zip(time_data,appliance_data.powers),
                        colour: colourPalette[(series.length+1)%colourCount],
                    });
                });
            });
        }
        return {
            series_list: series,
        };
    }

    return get_series_data;
}());


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
    document.getElementById('get_cust').innerHTML = json_data.headers.customer;
    document.getElementById('get_sts').innerHTML = json_data.headers.sts;
    document.getElementById('get_ets').innerHTML = json_data.headers.ets;
    document.getElementById('get_time').innerHTML = json_data.headers.time_unit;

    var str = json_data.headers.data_type;
    document.getElementById('data-heading').innerHTML = "imGate " + str.replace("_", " ");
}

///////////////////////////////////////////////////////////////////////////////

$( document ).ready(function() {

    $('#sdtpicker').datetimepicker(IMT.time.dtp_settings);
    $('#edtpicker').datetimepicker(IMT.time.dtp_settings);

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
