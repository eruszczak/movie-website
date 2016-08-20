function graph_genres() {
    selectValues = { "1": "test 1", "2": "test 2" };
    $("#mySelect").append(
      $.map(selectValues, function(v,k) {
         return $("<option>").val(k).text(v);
      })
    );
    link = '/api/g/'
     $.getJSON(link, {
          format: "json"
        }).done(function(data) {
            var names = $.map(data, function(dict) { return dict.name; });
            var values = $.map(data, function(dict) { return dict.the_count; });
            console.log(names)
            console.log(values)
            $('#graph').highcharts({
                xAxis: {
                    categories: names
                },
                series: [{
                    data: values
                }]
            });
        });
};

        function initialize_years(data) {
            var years = $.map(data, function(dict, year) { return year });
              years = years.sort(function(a, b){return b-a});
              years.unshift('all')
            $("#select_year").append(
              $.map(years, function(v, k) {
                 return $("<option>").val(k).text(v);
              })
            );
            initialize_years = function(){}
        }

function graph_months() {
    $('#select_year').show()
    link = '/api/month/'
     $.getJSON(link, {
          format: "json"
        }).done(function(data) {
            initialize_years(data)
            var selected_year = $("#select_year option:selected").text().toString();
            var months = $.map(data['2014'], function(dict, month) { return month });
            var values = $.map(data[selected_year], function(dict, month) { return dict.count });
            var series = []
            if (selected_year === 'all') {
                $('#select_year option').each(function() {
                    year = $(this).text()
                    if (year === 'all') { return true }
                    var values = $.map(data[year], function(dict, month) { return dict.count });
                    series.push({name: year, data: values})
                })
            } else {
                series.push({name: selected_year, data: values})
            }
            $('#graph').highcharts({
                title: {
                    text: 'Watched movies per month',
                    x: -20 //center
                },
                xAxis: {
                    categories: months
                },
                yAxis: {
                    title: {
                        text: 'Ratings'
                    },
                },
                tooltip: {
                    valueSuffix: ' ratings'
                },
                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle',
                    borderWidth: 0
                },
                series: series
            });
        });
};


function graph_rated() {
    link = '/api/rated/'
    $.getJSON(link, {
        format: "json"
    }).done(function(data) {
        var values = $.map(data, function(dict) { return dict.the_count });
        var rates = $.map(data, function(dict) { return dict.rate });
        $('#graph').highcharts({
            xAxis: {
                categories: rates
            },
            series: [{
                data: values
            }]
        });
    })
}

function graph_year() {
    link = '/api/year/'
    $.getJSON(link, {
        format: "json"
    }).done(function(data) {
        var values = $.map(data, function(dict) { return dict.the_count });
        var years = $.map(data, function(dict) { return dict.year });
        $('#graph').highcharts({
            xAxis: {
                categories: years
            },
            series: [{
                data: values
            }]
        });
    })
}


