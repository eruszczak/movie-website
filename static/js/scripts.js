$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();

    $("#summary").addClass('animated pulse');

    $(function () {
      $('[data-toggle="popover"]').popover()
    })

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
    link = '/charts/test'
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







$(document).ready(function() {
//    $('#unwatch').mouseover(function() {
//        $(this).val("want to see again").removeClass('unwatch-btn').addClass('watch-btn');
//    }).mouseout(function() {
//        $(this).val("don't want to see again").removeClass('watch-btn').addClass('unwatch-btn');
//    });
//
//    $('#watch').mouseover(function() {
//        $(this).val("don't want to see again").removeClass('watch-btn').addClass('unwatch-btn');
//    }).mouseout(function() {
//        $(this).val("want to see again").removeClass('unwatch-btn').addClass('watch-btn');
//    });

    $('#test_put').click(function() {
        console.log('xx')
        $.ajax({
            url : '/api/update/cro-minion-2015/',
            type: "PUT",
//            dataType : "json",
            success: function( data ){
            }
        });
        window.location.reload(true);
    })
});


// todo animation