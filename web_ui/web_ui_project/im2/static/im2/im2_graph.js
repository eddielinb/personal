/*
 *  imGate API
 *  comparison
 */

IMT.chart_settings = (function () {

    var options_aggregate = {
        chart: {
            renderTo: 'graphAggregate',
            type: 'line'
        },
        title: {
            text: 'Power consumption aggregate comparison'
        },
    };
    var options_compare = {
        title: {
            text: 'Power consumption comparison',
        },
        plotOptions: {
            area: {
                stacking: 'normal',
            },
        },
    };
    var chart_settings = [
        $.extend(true, {}, IMT.graph.options.power, options_aggregate),
    ];

    return chart_settings;

}());

get_data = (function (wave_data, chart) {

    var app_map = JSON.parse(django_app_map_string);
    var time_map = JSON.parse(django_time_map_string);
    var colourCount;
    var colourPalette = IMT.colour.getMany(colourCount);

    function get_series_data(wave_data, chart) {
        var title = "Aggregate consumption";
        var series=[];
        if (chart.options.chart.renderTo == 'graphAggregate') {
            $.each(wave_data, function(type_index, type_data) {
                $.each(type_data.data, function(zoom_index, data) {
                    var time_data = data.timestamps;
                    time_data = time_data.map(function(x) { return x * 1000; });
                    var power_data = data.root_powers;
                    series.push({
                        name: type_index.split('_')[0]+' '+time_map[data.time_unit_id],
                        data: IMT.zip(time_data,power_data),
                        colour: colourPalette[series.length%colourCount],
                    });
                });
            });
        } else {

            var div_str = chart.options.chart.renderTo;
            var div_char = div_str.substr(div_str.length - 1);
            var type_index = parseInt(div_char);
            var type_id = wave_data.estimated_data.data[0].appliance_types[type_index].appliance_type_id;

            title = app_map[type_id.toString()].name;

            var time_data = wave_data.estimated_data.data[0].timestamps;
            time_data = time_data.map(function(x) { return x * 1000; });

            $.each(wave_data.estimated_data.data[0].appliance_types[type_index].appliances, function(app_index, data) {
                var power_data = data.powers;
                series.push({
                    name: "estimated : "+data['appliance_id'],
                    data: IMT.zip(time_data,power_data),
                    colour: colourPalette[series.length%colourCount],
                    type: 'line'
                });
            });

            if (!!wave_data.observed_data.data[0].appliance_types[type_index]) {
                $.each(wave_data.observed_data.data[0].appliance_types[type_index].appliances, function(app_index, data) {
                    var power_data = data.powers;
                    series.push({
                        name: "observed "+type_index+" : "+data['appliance_id'],
                        data: IMT.zip(time_data,power_data),
                        colour: colourPalette[series.length%colourCount],
                        type: 'area'
                    });
                });
            }
        }
        return {
            title: title,
            series_list: series,
        };
    }

    return get_series_data;
}());

function ajax_success_callback(new_data){
    IMT.json_data=new_data;
    IMT.log(new_data, ["ajax", "callback"]);

    if ("calculation" in IMT.json_data)
    {
        populate_table_calculations(IMT.json_data);
    }
    else {
        $('.fetch').fadeToggle();
        populate_table(IMT.json_data);

        var $html = $(IMT.json_data.graph_html);
        $('.graph-populate').children('.graph-populate-panel').remove();
        $('.graph-populate').append($html);
        while (IMT.chart_settings.length > 1) {
            IMT.chart_settings.pop();
        }
        for (i = 0; i < IMT.json_data.graph_count; i++) {
            var options_compare = {
                chart: {
                    renderTo: 'graph' + i,
                },
            };
            var temp_settings = $.extend(true, {}, IMT.graph.options.power, options_compare);
            IMT.chart_settings.push(temp_settings);
            new Highcharts.Chart(temp_settings);
        }
        IMT.graph.graph_untrigger();
        IMT.graph.graph_trigger();

        var charts = Highcharts.charts;
        $.each(charts, function (chart_index, chart) {
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
}


function populate_table_calculations(json_data) {
    document.getElementById('get_f_measure').innerHTML = json_data.f_measure;
    document.getElementById('get_matching_rate').innerHTML = json_data.matching_rate;
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

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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
