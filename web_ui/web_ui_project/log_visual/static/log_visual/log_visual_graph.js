//
// Log visualisation graph
//

IMT.chart_settings = (function () {
    var option_unique_mac = {
        chart: {
            renderTo: 'graph_unique_mac'
        },
        title: {
            text: 'Unique Mac Log'
        }
    };

    var option_request = {
        chart: {
            renderTo: 'graph_request'
        },
        title: {
            text: 'Request Log'
        }
    }

    var chart_settings = [
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.xtime, option_unique_mac),
        $.extend(true, {}, IMT.graph.options.global, IMT.graph.options.sync_zoom, IMT.graph.options.xtime, option_request)
    ];
    return chart_settings;
}());

function get_data(log_data, chart){
    var series=[];
    var colourPalette = IMT.colour.getMany(4);
    var time_data = log_data.time_data;
    if (chart.options.chart.renderTo == 'graph_unique_mac')
    {
        time_data = time_data.map(function(x){ return x * 1000;});
        var mac_count = log_data.unique_mac_count;
        series.push({
            type: "column",
            name: "Unique Mac",
            data: IMT.zip(time_data, mac_count),
            colour: colourPalette[series.length]
        });
    }
    else if (chart.options.chart.renderTo == 'graph_request')
    {
        time_data = time_data.map(function(x){ return x * 1000;});
        var request_count = log_data.request_count;
        series.push({
            type: "column",
            name: "Request",
            data: IMT.zip(time_data, request_count),
            colour: colourPalette[series.length]
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

$( document ).ready(function(){
    IMT.graph.instantiate_charts(IMT.chart_settings);
    IMT.graph.post_data($('.graph_form'), { name: "data_type", value: django_populate_values_data_type },
                        django_post_url, ajax_success_callback, IMT.graph.ajax_error_callback);
});