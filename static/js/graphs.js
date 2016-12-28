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
                    name: 'Count',
                    data: values
                }]
            });
        });
};

function graph_months(chart, place='#graph') {
    $('#select_year').show()
     $.getJSON(chart.endpoint, {
            u: path_username
     }).done(function(data) {
        var series = [];
        for (var i = 0; i < data.length; i += 1) {
            // insert to series[] new year and 12-elems array filled with zeroes and replace value for that month
            // before inserting check if this year already is in series[]. is so, only replace zero
            var d = {};
            var year = data[i].year;
            var month = data[i].month;
            var count = data[i].the_count;
            var objIndex = findObjectInArray(series, year);

            if (objIndex > 0) {
                var curr_months = series[objIndex].data;
                curr_months[month - 1] = count;
                series[objIndex].data = curr_months;
            } else {
                d.name = year;
                d.data = [0,0,0,0,0,0,0,0,0,0,0,0];
                d.data[month - 1] = count;
                series.push(d);
            }
        }

        $(place).highcharts({
            chart: {
                type: 'column'
            },
            title: {
                text: chart.title,
                x: -20
            },
            xAxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            },
            yAxis: {
                title: {
                    text: chart.title
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
                                var url = '/explore/?u=' + path_username;
                                url += '&year=' + this.series.name + '&month=' + month_num;
                                window.open(url, '_blank');
                            }
                        }
                    }
                }
            },
            tooltip: {
                valueSuffix: ' ratings'
            },
            series: series
        });
     });
};


$(document).ready(function() {
//    graph_genres(charts.genres);
    $('#graph_genres').click();
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

function findObjectInArray(arr, val) {
    var index = -1;
    for (var j = 0; j < arr.length; j += 1) {
        if (arr[j].name == val) {
            index = j;
            break;
        }
    }
    return index;
}