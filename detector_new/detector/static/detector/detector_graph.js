//
// Detector Graph
//

IMT.chart_settings = (function () {
    var option_power = {
        chart:{
            renderTo: 'graph_power'
        },
        title:{
            text:'Power and estimated on'
        },
        plotOptions: {
            series: {
                events: {
                    click: function(e) {
                        onClickPowerUsage(Math.round(e.point.x / 1000.0));
                    }
                }
            }
        }

    };
    var option_prediction = {
        chart:{
            renderTo:'graph_prediction',
            type: 'line'
        },
        title:{
            text:'Prediction probability'
        },
        yAxis:{
            title:  {
                text: 'Threshold'
            },
            plotLines:[{
                value: threshold_value,
                color: "pink",
                dashStyle: "shortdash",
                width: 5,
                label: {
                    text:"threshold"
                }
            }]
        },
        plotOptions: {
            series: {
                events: {
                    click: function(e) {
                        onClickPowerUsage(Math.round(e.point.x / 1000.0));
                    }
                }
            }
        }
    };
    var option_waveforms = {
        chart:{
            renderTo:'graph_waveforms'
        },
        title:{
            text: 'waveforms'
        }
    };
    var option_diff = {
        chart:{
            renderTo:'graph_diff'
        },
        title:{
            text:'diff waveforms'
        }
    }
    var chart_settings =[
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.x, option_power),
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.x, option_prediction),
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.x, option_waveforms),
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.x, option_diff),
    ];
    return chart_settings;
}());

function onClickPowerUsage(ts){
    var charts = Highcharts.charts;
    //IMT.graph.post_data(ts, django_post_url, ajax_success_callback, IMT.graph.ajax_error_callback)
    post_data_wave(ts, django_post_url, ajax_success_callback_wave, IMT.graph.ajax_error_callback)
}

function post_data_wave(ts, url, success_callback, error_callback) {
    var charts = Highcharts.charts;
    $('.fetch').fadeToggle();
    $.each(charts, function(chart_index, chart) {
        c = $('.graph-div').eq(chart_index);
        IMT.graph.check_loading_chart(c);
    });

    // IMT.time.update_ts();
    IMT.xhr = $.ajax({
        type: "POST",
        url: url,
        data: {"ts":ts},
        dataType: "json",
        success: success_callback,
        error: error_callback
    });
}

function ajax_success_callback_wave (wave_data){
    IMT.json_data = wave_data
    IMT.log(wave_data, ["ajax", "callback"]);

    var charts = Highcharts.charts;
    populate_chart_waves(charts[2], wave_data, diff=false);
    populate_chart_waves(charts[3], wave_data, diff=true);
}

function populate_chart_waves (chart, wave_data, diff =false) {
    for (i = 0; i < wave_data.timestamps.length; i++) {
        {
            if (!diff) {
                if (!!chart.series[i]) {
                    chart.series[i].setData(wave_data.data.waveforms[i])
                }
                else {
                    chart.addSeries(
                        {
                            name: "waveforms",
                            data: wave_data.data.waveforms[i],
                            color: IMT.colour.get()
                        }
                    );
                }
            }
            else {
                if (!!chart.series[i])
                {
                    chart.series[i].setData(wave_data.data.diff[i])
                }
                else
                {
                chart.addSeries({
                    name: "diff",
                    data: wave_data.data.diff[i],
                    color: IMT.colour.get()
                });
                }
            }
        }
    }
}


function get_data(response_data, chart){
    var series=[];
    var colourPalette = IMT.colour.getMany(4);
    var time_data = response_data.timestamps;
    if (chart.options.chart.renderTo == 'graph_power')
    {
        time_data = time_data.map(function(x){ return x * 1000;});
        var power = response_data.data.root_powers;
        var estimated = response_data.data.estimated;
        series.push({
            name: "Power",
            data: IMT.zip(time_data, power),
            colour: colourPalette[series.length]
        });
        series.push({
            type: "area",
            name: "Estimated",
            data: IMT.zip(time_data, estimated),
            colour: IMT.colour.get()
        });
    }
    else if (chart.options.chart.renderTo == 'graph_prediction'){
        time_data = time_data.map(function(x){ return x * 1000;});
        var prediction_data = response_data.data.probability;
        series.push({
            name: "prediction",
            data: IMT.zip(time_data, prediction_data),
            colour: IMT.colour.get()
        });
    }
    else if (chart.options.chart.renderTo == 'graph_waveforms') {
        time_data = time_data.map(function (x) {
            return x * 1000;
        });
        var waveforms_data = response_data.data.waveforms;
        series.push({
            name: "waveforms",
            data: IMT.zip(time_data, waveforms_data),
            colour: IMT.colour.get()
        });
    }
    else if (chart.options.chart.renderTo == 'graph_diff') {
        time_data = time_data.map(function (x) {
            return x * 1000;
        });
        var diff_data = response_data.data.diff;
        series.push({
            name: "diff",
            data: IMT.zip(time_data, diff_data),
            colour: IMT.colour.get()
        });
    }
    return {
        series_list: series
    };
}

function ajax_success_callback(new_data){
    IMT.json_data = new_data;
    IMT.log(new_data, ["ajax", "callback"]);

    var charts = Highcharts.charts;
    $.each(charts, function(chart_index, chart) {
        if (!('data' in IMT.json_data)) {
            chart.showLoading("Error");
        } else if ('error' in IMT.json_data.data) {
            chart.showLoading(IMT.json_data.data['error']);
        } else {
            IMT.graph.load_chart($('.graph-div').eq(chart_index), true);
        }
        chart.zoom();
    });
}


$( document ).ready(function() {
    IMT.graph.instantiate_charts(IMT.chart_settings);
    IMT.graph.post_data(null, django_post_url, ajax_success_callback, IMT.graph.ajax_error_callback)
});