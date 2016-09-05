function school(link) {
     var question = document.getElementsByName("q")[0].value
     $('#question').html(question)
     $('#map').hide()

     $.getJSON(link, {
          format: "json"
     }).done(function(data) {
        if (typeof data === 'object') {
            initMap(data)
            $('#map').show()
//            data =
        }
        $('#answer').html(data)
        var item = $('<ul><li>' + question + '</li><li>' + data + '</li></ul>').hide().fadeIn(1500)
        $('#history').prepend(item)
     });
     $('input[type=text]').animate({ color: "red" }, 2000);
//     document.getElementsByName("q")[0].value = ''
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


//function initMap() {
//    var mapDiv = document.getElementById('map');
//    var map = new google.maps.Map(mapDiv, {
//        center: {lat: 44.540, lng: -78.546},
//        zoom: 8
//    });
//}
function initMap(data) {
    var myLatLng = {lat: data.lat, lng: data.lng};
//    $('#map').show()
// hide after
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 6,
      center: myLatLng
    });

    var marker = new google.maps.Marker({
      position: myLatLng,
      map: map,
      title: data.place             /////
    });
}
