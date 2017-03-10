$(document).ready(function() {

    /* display graphs for AllYears and AllGenres pages */
    if ($('div').is('#includeChartGenres')) {
        renderChart(charts.genres, '#includeChartGenres');
    }

    if ($('div').is('#includeChartYears')) {
        renderChart(charts.years, '#includeChartYears');
    }

    $('#graph_genres').click(function(e) {
        renderChart(charts.genres);
    });

    $('#graph_year').click(function(e) {
        renderChart(charts.years);
    });

    $('#graph_rated').click(function(e) {
        renderChart(charts.rates);
    });

    $('#graph_months').click(function(e) {
        monthlyChart(charts.monthly);
    });

    $('#graph_genres').trigger('click');
});


function renderChart(chart, place) {
    place = place || '#graph';
//function renderChart(chart, place) {
    /*If rendered in different place than #graph it means that I want global data, not for specific user*/
    var queryParams = place === '#graph' ? {u: path_username} : {};
//    var queryParams = place ? {u: path_username} : {};
//    var queryParams = {u: path_username};
     $.getJSON(chart.endpoint, queryParams).done(function(data) {
            if ('data_rates' in data) {
                data = data['data_rates'];
            }
            var categories = $.map(data, function(dict) { return dict[chart.fieldName]; });
            var values = $.map(data, function(dict) { return dict.the_count; });
            $(place).highcharts({
                title: {
                    text: place === '#graph' ? chart.title : chart.title.replace('Rating', 'Title'),
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
                        enableMouseTracking: true,
                        animation: false

                    },
                    series: {
                        cursor: 'pointer',
                        point: {
                            events: {
                                click: function () {
                                    if (place === '#graph') {
                                        var url = '/explore/?u=' + path_username + '&' + chart.queryParam + this.category;
                                    } else {
                                        var url = '/explore/?' + chart.queryParam + this.category;
                                    }
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

function monthlyChart(chart, place) {
    place = place || '#graph';
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

            if (objIndex > -1) {
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
                animation: false,
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

charts = {
    'genres': {
        'endpoint': '/api/g/',
        'title': 'Rating Distribution By Genre',
        'fieldName': 'genre__name',
        'queryParam': 'g=',
    },
    'years': {
        'endpoint': '/api/y/',
        'title': 'Rating Distribution By Year',
        'fieldName': 'year',
        'queryParam': 'y=',
    },
    'rates': {
        'endpoint': '/api/r/',
        'title': 'Rating Distribution',
        'fieldName': 'rate',
        'queryParam': 'r=',
    },
    'monthly': {
        'endpoint': '/api/m/',
        'title': 'Watched per month',
    },
}

var pathArray = window.location.pathname.split('/');
var path_username = pathArray[2];