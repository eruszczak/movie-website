var pathArray = window.location.pathname.split('/');
var path_username = pathArray[2];

charts = {
    'genres': {
        'endpoint': '/api/ratings/g/',
        'chartTitle': 'Rating Distribution By Genre',
        'fieldName': 'genre__name',
        'detail_url': '',
//        'params': {'u': path_username}
    },
    'years': {
        'endpoint': '/api/ratings/y/',
        'chartTitle': 'Rating Distribution By Year',
        'fieldName': 'year',
//        'detail_url': '',
//        'params': {'u': path_username}
    },
    'rates': {
        'endpoint': '/api/ratings/r/',
        'chartTitle': 'Rating Distribution',
        'fieldName': 'rate',
//        'detail_url': '',
//        'params': {'u': path_username}
    },
    'monthly': {
        'endpoint': '/api/ratings/m/',
        'chartTitle': 'Watched per month',
        'fieldName': 'month',
//        'detail_url': '',
//        'params': {'u': path_username, ''}
    },
}

// todo
// clicked btn effect on default chart
// details

function graph_genres(chart, place='#graph') {
     $.getJSON(chart.endpoint, {
//          format: 'json',
          u: path_username
        }).done(function(data) {
            var categories = $.map(data, function(dict) { return dict[chart.fieldName]; });
            var values = $.map(data, function(dict) { return dict.the_count; });
            $(place).highcharts({
                title: {
                    text: chart.chartTitle,
                    x: -20 //center
                },
                xAxis: {
                    categories: categories
                },
                legend: {
                    enabled: false
                },
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: true
                    },
                    series: {
                        cursor: 'pointer',
                        point: {
                            events: {
                                click: function () {
                                    var url = '/genre/' + this.category
                                    window.open(url, '_blank')
                                }
                            }
                        }
                    }
                },
                series: [{
                    data: values
                }]
            });
        });
};

/*
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

function graph_months(place='#graph') {
    $('#select_year').show()
    link = '/api/month/'
     $.getJSON(link, {
          format: "json"
        }).done(function(data) {
            initialize_years(data)
            var series = []
            var months = $.map(data['2014'], function(dict, month) { return month });
            var years = $.map(data, function(dict, year) { return year });
            for (var i = 0; i < years.length; i += 1) {
                var values = $.map(data[years[i]], function(dict, month) { return dict.count });
                series.push({name: years[i], data: values})
            }
            $(place).highcharts({
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Watched per month',
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
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: true
                    },
                    series: {
                        cursor: 'pointer',
                        point: {
                            events: {
                                click: function () {
                                    var month_num = parseInt(this.index) + 1
                                    var url = '/' + this.series.name + '/' + month_num
                                    window.open(url, '_blank')
                                }
                            }
                        }
                    }
                },
                tooltip: {
                    valueSuffix: ' ratings'
                },
//                legend: {
//                    layout: 'vertical',
//                    align: 'right',
//                    verticalAlign: 'middle',
//                    borderWidth: 0
//                },
                series: series
            });
        });
};



*/
$(document).ready(function() {
    graph_genres(charts.genres);
});
$('#graph_genres').click(function() {
    graph_genres(charts.genres);;
});
$('#graph_year').click(function() {
    graph_genres(charts.years);
});
$('#graph_rated').click(function() {
    graph_genres(charts.rates);
});
$('#graph_months').click(function() {
    graph_genres(charts.monthly);
});

/* display graphs for AllYears and AllGenres pages */
/*$(function(){ todo
    if ($('div').is('#include_graph_genre')) {
        graph_genres('#include_graph_genre')
    }
    if ($('div').is('#include_graph_year')) {
        graph_year('#include_graph_year')
    }
});*/