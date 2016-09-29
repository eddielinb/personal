/*
 *  Shared graph functions
 *
 */

IMT.graph = (function () {

    function instantiate_charts(inst_chart_settings) {
        $.each(inst_chart_settings, function(chart_index, chart_options) {
            IMT.logg(inst_chart_settings, "Chart options");
            IMT.logg(chart_options, "Chart options");
            IMT.logg(chart_options.chart, "Chart options");
            // IMT.logg(chart_options.chart.renderTo, "Chart options");
            var temp_chart = new Highcharts.Chart($.extend(true, {}, chart_options));
        });
    }

    function get_app_powers(json_data) {
        var zip_data = [];
        $.each(json_data.data, function(index, data) {
            power_data = data.root_powers;
            time_data = data.timestamps;
            time_data = time_data.map(function(x) { return x * 1000; });
            zip_data.push(IMT.zip(time_data,power_data));
        });
        return zip_data;
    }

    function post_data(form_el, data_type_tuple, url, success_callback, error_callback) {

        IMT.log(form_el, ["post_data"]);

        var charts = Highcharts.charts;
        $('.fetch').fadeToggle();
        $.each(charts, function(chart_index, chart) {
            c = $('.graph-div').eq(chart_index);
            check_loading_chart(c);
        });

        IMT.time.update_ts();

        var form_data = form_el.serializeArray();
        form_data.push(data_type_tuple);

        IMT.xhr = $.ajax({
            type: "POST",
            url: url,
            data: jQuery.param(form_data),
            dataType: "json",
            success: success_callback,
            error: error_callback
        });
    }

    function populate_chart(chart) {



        var chart_data = get_data(IMT.json_data.wave_data, chart);

        chart.setTitle( {text: chart_data.title} );

        while(chart.series.length > 0)
            chart.series[0].remove(true);
        for (i = 0; i < chart_data.series_list.length; i++)
        {
            chart.addSeries(chart_data.series_list[i]);
        }
    }

    function check_loading_chart(chart_object) {
        if (chart_object.parent().parent().hasClass("in")) {
            chart_object.addClass("graph-loading");
            loading_chart(chart_object);
        }
    }

    function loading_chart(chart_object) {
        if (chart_object.hasClass("graph-loading") || (chart_object.hasClass("graph-loaded"))) {
            chart_object.highcharts().showLoading();
            if (chart_object.hasClass("graph-loading")) {
                var chart_object_parent = chart_object.parent().parent().parent();
                chart_object_parent.removeClass("panel-default");
                chart_object.removeClass("graph-loaded");
                chart_object.addClass("graph-loading");
                chart_object_parent.addClass("panel-danger");
            }
        }
    }

    function load_chart(chart_object, loaded_populate) {
        if (!!IMT.json_data) {
            var chart_object_parent = chart_object.parent().parent().parent();
            var populating_bool = (chart_object.hasClass("graph-loaded") || chart_object.hasClass("graph-loading"));
            // if (populating_bool) {
            // }
            if(chart_object.hasClass("graph-loaded")) {
                if (loaded_populate)
                    populate_chart(chart_object.highcharts());
                chart_object_parent.removeClass("panel-danger").addClass("panel-default");
            } else if (chart_object.hasClass("graph-loading")) {
                populate_chart(chart_object.highcharts());
                chart_object.removeClass("graph-loading");
                chart_object.addClass("graph-loaded");
                chart_object_parent.removeClass("panel-danger").addClass("panel-default");
            }
            if (populating_bool) {
                $('html,body').animate({
                    scrollTop: chart_object_parent.offset().top
                }, 200);
                chart_object.highcharts().hideLoading();
            }
        }
    }

    function ajax_error_callback() {
        $.each(Highcharts.charts, function(chart_index, chart) {
            chart.showLoading("Error");
            chart.zoom();
        });
    }

    function collapse_trigger() {
        $('.graph-div').parent().parent().on('show.bs.collapse', function(e){
            IMT.log($( this ), ["collapse", "show"]);
            c = $( this ).find('.graph-div');
            if (!c.hasClass("graph-loaded"))
                c.addClass("graph-loading");
            IMT.graph.loading_chart(c);
        });
        $('.graph-div').parent().parent().on('shown.bs.collapse', function(e){
            IMT.log($( this ), ["collapse", "shown"]);
            c = $( this ).find('.graph-div');
            c.highcharts().reflow();
            IMT.graph.load_chart(c, false);
        });
    }


    /********************************************************************
     * Synchronizing charts                                             *
     * http://www.highcharts.com/demo/synchronized-charts               *
     ********************************************************************/
    /**
     * In order to synchronize tooltips and crosshairs, override the
     * built-in events with handlers defined on the parent element.
    */

    var hoverElem;
    function get_hover(e) {
        hoverElem = $( this ).attr('id');
        // IMT.log(hoverElem, ["get_hover"]);
    }
    function sync_hover(e) {
        var hover_chart,
            point,
            points,
            event,
            ts;
        if (!!hoverElem) {
            hover_chart = $('#'+hoverElem).highcharts();
            event = hover_chart.pointer.normalize(e.originalEvent); // Find coordinates within the chart
            points=[];
            $.each(hover_chart.series, function(series_index, series) {
                if (!!series) {
                    points[series_index] = series.searchPoint(event, true); // Get the hovered point
                }
            });
            points.sort(function(a,b) {return a.dist - b.dist;});
            point = points[0];
            if (point) {
                point.highlight(e);
                ts = point.x;
                $( this ).find('.graph-div').each(function(index){
                    if ($( this ).hasClass("graph-loaded")) {
                        if (!($( this ).attr('id') === hoverElem)) {
                            var chart = $( this ).highcharts();
                            event = chart.pointer.normalize(e.originalEvent); // Find coordinates within the chart
                            point = chart.series[0].data.filter(function ( obj ) { // Get the hovered point
                                return obj.x === ts;
                            })[0];
                            if (point) {
                                point.highlight(e);
                            }
                        }
                    }
                });
            }
        }
    }
    function hover_trigger() {
        $('.graph-div').on('mouseenter', get_hover);
        $('.graph-sync').bind('mousemove touchmove touchstart', sync_hover);
    }

    function graph_trigger() {
        collapse_trigger();
        hover_trigger();
    }
    function graph_untrigger(){
        $('.graph-div').unbind('mouseenter');
        $('.graph-sync').unbind('mousemove touchmove touchstart');
        $('.graph-div').parent().parent().unbind('show.bs.collapse');
        $('.graph-div').parent().parent().unbind('shown.bs.collapse');
    }

    /**
     * Synchronize zooming through the setExtremes event handler.
     */
    function syncExtremes(e) {
        var thisChart = this.chart;
        if (e.trigger !== 'syncExtremes') { // Prevent feedback loop
            Highcharts.each(Highcharts.charts, function (chart) {
                if (!!chart.options.xAxis[0].events) {  // Check chart is active
                    if (chart !== thisChart) { // Check not activating chart
                        if (chart.xAxis[0].setExtremes) { // It is null while updating
                            chart.xAxis[0].setExtremes(e.min, e.max, undefined, false, { trigger: 'syncExtremes' });
                        }
                    }
                }
            });
        }
    }

    return {
        instantiate_charts: instantiate_charts,
        get_app_powers: get_app_powers,
        post_data: post_data,
        populate_chart: populate_chart,
        check_loading_chart: check_loading_chart,
        loading_chart: loading_chart,
        load_chart: load_chart,
        ajax_error_callback: ajax_error_callback,
        // collapse_trigger: collapse_trigger,
        // hover_trigger: hover_trigger,
        graph_trigger: graph_trigger,
        graph_untrigger: graph_untrigger,
        syncExtremes: syncExtremes,
    };
}());

/**
 * Override the reset function, we don't need to hide the tooltips and crosshairs.
 */
//Highcharts.Pointer.prototype.reset = function () {
//    return undefined;
//};

/**
 * Highlight a point by showing tooltip, setting hover state and draw crosshair
 */
Highcharts.Point.prototype.highlight = function (event) {
    this.onMouseOver(); // Show the hover marker
    this.series.chart.tooltip.refresh(this); // Show the tooltip
    this.series.chart.xAxis[0].drawCrosshair(event, this); // Show the crosshair
};
//********************************************************************


$( document ).ready(function() {

    /********************************************************************
     * Synchronizing charts                                             *
     * http://www.highcharts.com/demo/synchronized-charts               *
     ********************************************************************/

    IMT.graph.graph_trigger();

});
