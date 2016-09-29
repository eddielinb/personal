/*
 *  Graph Settings
 *  Contains various graph options
 */

IMT.graph = (function (my_graph) {

    my_graph.options = (function () {

        // Global options
        var graph_options_global = {
            legend: {
                enabled: true
            },
            credits: {
                text: "Informetis - Highcharts",
            },
            tooltip: {
                valueDecimals: 2,
            },
        };

        // x axis zoom
        var graph_options_xzoom = {
            chart: {
                zoomType: 'x'
            },
            subtitle: {
                text: document.ontouchstart === undefined ?
                        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
        };

        // time axis
        var graph_options_xtime = {
            xAxis: {
                type: 'datetime',
            },
        };

        var graph_options_x = $.extend(true, {}, graph_options_xtime, graph_options_xzoom);

        var graph_options_sync_zoom = {
            xAxis: {
                events: {
                    setExtremes: IMT.graph.syncExtremes
                },
            },
        };

        var graph_options_power = {
            yAxis: {
                title: {
                    text: 'Power'
                }
            },
        };
        var graph_options_global_power = $.extend(true, {}, graph_options_global, graph_options_sync_zoom, graph_options_x, graph_options_power);

        var graph_options_1 = {
            chart: {
                renderTo: 'graph1',
                type: 'area'
            },
            title: {
                text: 'Power consumption aggregate'
            },
        };

        var graph_options_2 = {
            chart: {
                renderTo: 'graph2',
                type: 'line'
            },
            title: {
                text: 'Power consumption by appliance'
            },
        };

        var graph_options_3 = {
            chart: {
                renderTo: 'graph3',
                type: 'area'
            },
            title: {
                text: 'Power consumption by appliance stacked'
            },
            plotOptions: {
                area: {
                    stacking: 'normal'
                }
            }
        };

        return {
            global: graph_options_global,
            xzoom: graph_options_xzoom,
            xtime: graph_options_xtime,
            x: graph_options_x,
            sync_zoom: graph_options_sync_zoom,
            power: graph_options_global_power,
            v1: graph_options_1,
            v2: graph_options_2,
            v3: graph_options_3,
        };
    }());

    return my_graph;
}(IMT.graph));
