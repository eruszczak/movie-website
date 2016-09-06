function school(link) {
     $('#result-panel, .result-panel-heading, #inputQuery:focus').css('border-color', getRandomColor())
//     $('#inputQuery:focus').css('border-color', getRandomColor())
     var question = document.getElementsByName("q")[0].value
     if (!question) { return }
     $('#question').html(question)

     if ($('#map').is(":visible")) {
        $('#map').hide()
     }
     if ($('#query_info').is(":visible")) {
        $('#query_info').hide()
     }

     $.getJSON(link, {
          format: "json"
     }).done(function(data) {
        if (!data) {
            $('#query_info').show().html('An error occurred. Try again')
            return
        }
        if (typeof data === 'object') {
            initMap(data)
            $('#map').show()
            data =  data.time
        }
        $('#answer').html(data)
        var item = $('<ul><li>' + question + '</li><li>' + data + '</li></ul>').hide().fadeIn(1000)
        $('#history').prepend(item)
     });
     document.getElementsByName("q")[0].value = ''
};

function get_link() {
    query = document.getElementsByName("q")[0].value;
    link = '/api-school/?q=' + query
    return link
}

$('#school').on('click', function() {
    link = get_link()
    school(link)
})

$('#inputQuery').keypress(function(e) {
    if (e.which == 13) {
        link = get_link()
        school(link)
        return false;
    }
})

function initMap(data) {
    var myLatLng = {lat: data.lat, lng: data.lng};
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 6,
      center: myLatLng
    });

    var marker = new google.maps.Marker({
      position: myLatLng,
      map: map,
      title: data.place
    });
}


document.getElementsByName("q")[0].value = 'time new york'  // todo



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
    //getting the next element
    $content = $header.next();
    console.log($header, $content)
    //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
    $content.slideToggle(500, function () {
        //execute this after slideToggle is done
        //change text of header based on visibility of content div
//        $header.text(function () {
//            //change text based on condition
//            return $content.is(":visible") ? "Collapse" : "Expand";
//        });
    });

});