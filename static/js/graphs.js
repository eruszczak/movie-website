var pathArray = window.location.pathname.split('/');
var path_username = pathArray[2];

charts = {
    'genres': {
        'endpoint': '/api/ratings/g/',
        'title': 'Rating Distribution By Genre',
        'fieldName': 'title__genre__name',
        'detail_url': '&g=',
    },
    'years': {
        'endpoint': '/api/ratings/y/',
        'title': 'Rating Distribution By Year',
        'fieldName': 'title__year',
        'detail_url': '&y=',
    },
    'rates': {
        'endpoint': '/api/ratings/r/',
        'title': 'Rating Distribution',
        'fieldName': 'rate',
        'detail_url': '&r=',
    },
    'monthly': {
        'endpoint': '/api/ratings/m/',
        'title': 'Watched per month',
    },
}

// todo
// clicked btn effect on default chart
// details

function graph_genres(chart, place='#graph') {
     $.getJSON(chart.endpoint, {
          u: path_username
        }).done(function(data) {
            var categories = $.map(data, function(dict) { return dict[chart.fieldName]; });
            var values = $.map(data, function(dict) { return dict.the_count; });
            $(place).highcharts({
                title: {
                    text: chart.title,
                    x: -20
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
                                    var url = '/explore/?u=' + path_username + chart.detail_url + this.category;
                                    window.open(url, '_blank');
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
    years.unshift('all');
    $("#select_year").append(
        $.map(years, function(v, k) {
            return $("<option>").val(k).text(v);
        })
    );
    initialize_years = function(){};
}
*/
function graph_months(chart, place='#graph') {
    $('#select_year').show()
     $.getJSON(chart.endpoint, {
            u: path_username
        }).done(function(data) {
//            initialize_years(data);
            var series = [];
            var months = $.map(data['2014'], function(dict, month) { return month });
            var years = $.map(data, function(dict, year) { return year });
            for (var i = 0; i < years.length; i += 1) {
                var values = $.map(data[years[i]], function(dict, month) { return dict.count });
                series.push({name: years[i], data: values});
            };
            $(place).highcharts({
                chart: {
                    type: 'column'
                },
                title: {
                    text: chart.title,
                    x: -20
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
                                    var month_num = parseInt(this.index) + 1;
                                    var url = '/' + this.series.name + '/' + month_num;
                                    window.open(url, '_blank');
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
    graph_months(charts.monthly);
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