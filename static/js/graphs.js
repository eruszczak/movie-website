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
        console.log(data)
            initialize_years(data)
            var selected_year = $("#select_year option:selected").text().toString();
            var months = $.map(data[selected_year], function(dict, month) { return month });
            var values = $.map(data[selected_year], function(dict, month) { return dict.count });
            $('#graph').highcharts({
            xAxis: {
                categories: months
            },
            series: [{
                data: values
            }]
        });
    });
};
