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
        var resource_name = $(location).attr('pathname').split('/')[2];
        $.ajax({
            type: "PUT",
            url : '/api/update/' + resource_name + '/',
            dataType : "json",
            success: function( data ) {
            }
        });
        window.location.reload(true);
    })

    $('.test_put2').click(function() {
        console.log('x')
//        var resource_name = $(location).attr('pathname').split('/')[2];
//        $.ajax({
//            type: "PUT",
//            url : '/api/update/' + resource_name + '/',
//            dataType : "json",
//            success: function( data ) {
//            }
//        });
//        window.location.reload(true);
    })
});


// todo animation

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function send_changed_order(data) {
    $.ajax({
    data: {
        item_order: data,
        csrfmiddlewaretoken: csrftoken
    },
    type: 'POST',
    url: '/favourites/'
    });
}

$( function() {
    $('#sortable').sortable({
        placeholder: 'sort-placeholder',
        axis: 'y',
        update: function (event, ui) {
            $('#save-order').removeClass('disabled');
            var data = $(this).sortable('serialize');
            $(this).find('li').each(function(i){
                $(this).find('p.item-order').text(i+1);
            });
            send_changed_order(data);
        }
    });
    $( "#sortable" ).disableSelection();
});

$('#save-order').click(function() {
    var data = $('#sortable').sortable('serialize');
    send_changed_order(data);
      // $(document).ajaxStop(function () {
          window.location.reload(false);
    // });
});