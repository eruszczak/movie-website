$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();

    $("#summary").addClass('animated pulse');

    $( "#clickme" ).click(function() {
      $( "#book" ).fadeOut( "slow", function() {
        // Animation complete
      });
      });

    $("#sendQuery").on("click", function () {
        getResults();
    });

});

function getResults() {
    link = 'http://127.0.0.1:8000/charts/test'
     $.getJSON(link, {
          format: "json"
        }).done(function(data) {
            $('#highcharts').highcharts({
            xAxis: {
                categories: data.months
            },

            series: [{

                data: data.values
            }]
        });
    });
};