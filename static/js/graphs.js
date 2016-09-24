function graph_genres(place='#graph') {
    link = '/api/g/'
     $.getJSON(link, {
          format: "json"
        }).done(function(data) {
            var names = $.map(data, function(dict) { return dict.name; });
            var values = $.map(data, function(dict) { return dict.the_count; });
            $(place).highcharts({
                title: {
                    text: 'Rating Distribution By Genre',
                    x: -20 //center
                },
                xAxis: {
                    categories: names
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


function graph_rated(place='#graph') {
    link = '/api/rated/'
    $.getJSON(link, {
        format: "json"
    }).done(function(data) {
        var values = $.map(data, function(dict) { return dict.the_count });
        var rates = $.map(data, function(dict) { return dict.rate });
        $(place).highcharts({
            title: {
                text: 'Rating Distribution',
                x: -20 //center
            },
            xAxis: {
                categories: rates
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
                                var url = '/rated/' + this.category
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
    })
}

function graph_year(place='#graph') {
    link = '/api/year/'
    $.getJSON(link, {
        format: "json"
    }).done(function(data) {
        var values = $.map(data, function(dict) { return dict.the_count });
        var years = $.map(data, function(dict) { return dict.year });
        $(place).highcharts({
            title: {
                text: 'Rating Distribution By Year',
                x: -20 //center
            },
            xAxis: {
                categories: years
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
                                var url = '/year/' + this.category
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
    })
}
graph_months();
// $( document ).ready(function() {
//     $("#graph_months").click();
// });

$('#graph_rated').click(function() {
    graph_rated()
});
$('#graph_year').click(function() {
    graph_year()
});
$('#graph_months').click(function() {
    graph_months()
});
$('#graph_genres').click(function() {
    graph_genres()
});

/* display graphs for AllYears and AllGenres pages */
$(function(){
    if ($('div').is('#include_graph_genre')) {
        graph_genres('#include_graph_genre')
    }
    if ($('div').is('#include_graph_year')) {
        graph_year('#include_graph_year')
    }
});