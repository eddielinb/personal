/*
 *  Google Drive
 *
 */

IMT.chart_settings = (function () {

    var options_power = {
        chart: {
            renderTo: 'graph_power',
            type: 'line',
            load: function() {
                chart = this;
            }
        },
        title: {
            text: 'Power consumption'
        },
        yAxis: {
            title: {
                text: 'power'
            }
        },
        plotOptions: {
            series: {
                events: {
                    click: function(e) {
                        onClickedPowerUsage(Math.round(e.point.x / 1000.0));
                    }
                }
            },
        },
    };
    var options_rssi = {
        chart: {
            renderTo: 'graph_rssi',
            type: 'line'
        },
        yAxis: {
            title: {
                text: 'rssi'
            }
        },
        title: {
            text: 'RSSI'
        },
    };
    var options_voltages = {
        chart: {
            renderTo: 'graph_wave_v',
            type: 'line'
        },
        title: {
            text: 'Voltage'
        },
        subtitle: {
            text: 'Click a power point to see the waveform'
        },
        yAxis: {
            title: {
                text: 'voltage'
            }
        },
    };
    var options_currents = {
        chart: {
            renderTo: 'graph_wave_i',
            type: 'line'
        },
        subtitle: {
            text: 'Click a power point to see the waveform'
        },
        title: {
            text: 'Currents'
        },
        yAxis: {
            title: {
                text: 'current'
            }
        },
    };
    var chart_settings = [
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.x, options_power),
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.x, options_rssi),
        $.extend(true, {}, IMT.graph.options.global, options_voltages),
        $.extend(true, {}, IMT.graph.options.global, options_currents),
    ];

    return chart_settings;

}());

function onClickedPowerUsage(ts) {
    var charts = Highcharts.charts;
    $('#graph_wave_v').parent().parent().collapse("show");
    $('#graph_wave_i').parent().parent().collapse("show");
    populate_chart_wave(charts[2], ts);
    populate_chart_wave(charts[3], ts);
}

function populate_chart_wave(chart, ts) {
    var series_data = get_data_wave(IMT.json_data.wave_data, chart, ts);
    for (i = 0; i < series_data.series_list.length; i++)
    {
        if (!!chart.series[i])
            chart.series[i].setData(series_data.series_list[i].data);
        else
            chart.addSeries(
                {
                    name: series_data.series_list[i].name,
                    data: series_data.series_list[i].data,
                    color: series_data.series_list[i].colour,
                }
            );
    }
}

function get_data(wave_data, chart) {
    var series=[];
    var colourPalette = IMT.colour.getMany(4);
    var time_data = wave_data.timestamps;
    if (chart.options.chart.renderTo == 'graph_power') {
        time_data = time_data.map(function(x) { return x * 1000; });
        $.each(wave_data.data, function(channel_index, data) {
            var power_data = data.root_powers;
            series.push({
                name: "Channel " + data.channel,
                data: IMT.zip(time_data,power_data),
                colour: colourPalette[series.length]
            });
        });
    } else if (chart.options.chart.renderTo == 'graph_rssi') {
        time_data = time_data.map(function(x) { return x * 1000; });
        var rssi_data = wave_data.rssi;
        series.push({
            name: "RSSI",
            data: IMT.zip(time_data,rssi_data),
            colour: IMT.colour.get(),
        });
    }
    return {
        series_list: series,
    };
}

function get_data_wave(wave_data, chart, ts) {
    var series=[];
    var colourPalette = IMT.colour.getMany(4);
    var ts_index=wave_data.timestamps.indexOf(ts);
    if (chart.options.chart.renderTo == 'graph_wave_v') {
        var v_data = wave_data.voltages[ts_index];
        series.push({
            name: "V",
            data: v_data,
            colour: IMT.colour.get(),
        });
    } else if (chart.options.chart.renderTo == 'graph_wave_i') {
        $.each(wave_data.data, function(channel_index, data) {
            var i_data = data.waves[ts_index];
            series.push({
                name: "L" + (channel_index+1),
                data: i_data,
                colour: colourPalette[series.length]
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
    document.getElementById('get_mac').innerHTML = json_data.headers.mac;
    document.getElementById('get_sts').innerHTML = json_data.headers.sts;
    document.getElementById('get_ets').innerHTML = json_data.headers.ets;

    var str = json_data.headers.data_type;
    document.getElementById('data-heading').innerHTML = "Google drive " + str.replace("_", " ");
}

///////////////////////////////////////////////////////////////////////////////

$( document ).ready(function() {

    $('#sdtpicker').datetimepicker(IMT.time.dtp_settings);
    $('#edtpicker').datetimepicker(IMT.time.dtp_settings);

    IMT.graph.instantiate_charts(IMT.chart_settings);

    IMT.graph.post_data($('.graph_form'), { name: "data_type", value: django_populate_values_data_type }, django_post_url, ajax_success_callback, IMT.graph.ajax_error_callback);

});
