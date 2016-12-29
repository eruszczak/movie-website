$question = document.getElementsByName("q")[0]

function school(link) {
     $('#result-panel, .result-panel-heading, #inputQuery:focus, .functionality').css('border-color', getRandomColor())

     var question = $question.value;
     if (!question) { return; };
     $('#question').html(question);

    change_display()

     $.getJSON(link, {
          format: "json"
     }).done(function(data) {
        if (!data) {
            $('#query_info').show().html('An error occurred. Try again');
            return;
        }
        if (typeof data === 'object') {
            $('#map').show();
            initMap(data);
            data =  data.time;
        }
        $('#answer').html(data)
        var item = $('<ul><li>' + question + '</li><li>' + data + '</li></ul>').hide().fadeIn(1000);
        $('#history').prepend(item);
     });
     $question.value = '';
};

function get_link() {
    query = document.getElementsByName("q")[0].value;
    link = '/api-school/?q=' + query;
    return link;
}

$('#school').on('click', function() {
    link = get_link()
    school(link)
})

$('#inputQuery').keypress(function(e) {
    if (e.which == 13) {
        link = get_link();
        school(link);
        return false;
    }
})

var map;
function initMap(data) {
    if (data) {
        var myLatLng = {lat: data.lat, lng: data.lng};
        map = new google.maps.Map(document.getElementById('map'), {
            zoom: 6,
            center: myLatLng
        });

        var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            title: data.place
        });
    }
}


function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getRandomColor() {
    var r = getRandomInt(0, 255);
    var g = getRandomInt(0, 255);
    var b = getRandomInt(0, 255);
    return "rgb(" + r + "," + g + "," + b + ")"
}



$(".functionality").click(function () {
    $header = $(this);
    $content = $header.next();
    $content.slideToggle(500, function () {
    });
});


function change_display() {
     if ($('#map').is(":visible")) {
        $('#map').hide()
     }
     if ($('#query_info').is(":visible")) {
        $('#query_info').hide()
     }
     if ($('#answer').is(":hidden")) {
        $('#answer').fadeIn(1000)
     }
}