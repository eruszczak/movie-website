$('#go').on('click', function() {
    getResults();
});

function redirect_to_first_page() {


    redirect_to_first_page = function(){}
}

function per_page() {
    var page_size = $("#select_per_page option:selected").text()//.toString();

    console.log(page_size)
    if (page_size) {
        getResults(null, page_size)
    }
}

function getResults(new_link = null, selected_per_page = false) {
    if (new_link === null) {
        link = '/api/?'
        //    $(".content").empty(); // link += '&callback=?';
        //    document.getElementsByName("title")[0].value = '';  //    document.getElementsByName("year")[0].value = '';
        title = document.getElementsByName("q")[0].value;
        year = document.getElementsByName("year")[0].value;
        if (!year && !title) { return; }
        if (title) {
            link += 'q=' + title
        }
        if (selected_per_page) {
            link += '&per_page=' + selected_per_page
        }
    } else {
        link = new_link
    }
    call_api(link);
}

function call_api(link) {
    $("#content table").empty();
    var get_page = /(?:\?page=)(\d+)/.exec(link)
    if (get_page) { get_page = get_page[1] - 1 } else { get_page = 0 }

    var get_page_size = /(?:per_page=)(\d+)/.exec(link)
    if (get_page_size) { get_page_size = get_page_size[1] } else { get_page_size = 20 }

    $.getJSON(link, {
//      format: "json"
    }).done(function(data) {
        $.each(data.results, function(count, item) {
//            console.log(get_page, get_page_size, get_page*get_page_size, count)
//            $('.content table tbody').append('<tr>' + '<td>' + get_page * get_page_size + count + 1 + '</td><td>' + item.name + '</td><td>' +
//            item.rate + '</td></tr>')
            if (!item.watch_again_date) {
                var btn = 'w'
                var type = 'watch'
                var value = "don't want to see again"
            } else {
                var btn = 'un'
                var type = 'unwatch'
                var value = 'want to see again'
            }
            // <input type="button" id="buttonId" name="_mail" value="Enviar Mail">
             var input = '<button id="' + btn + '" class="btn btn-sm see-again-btn ' + type + '-btn" type="button">Go!</button>'
//            var input = '<input id="' + btn + '" class="btn btn-sm see-again-btn ' + type + '-btn" type="button" value="' + value + '" />'
            $('#content table').append('<tr><td>' + item.name + '</td><td>' + input + '</td></tr>')
        });
        if (data.previous === null && data.next === null) {
            $('#pagination').hide()
        } else {
            $('#pagination').show()
            if (data.previous === null) {
                $('.previous').hide()
            } else {
                $('.previous').show()
            }
            if (data.next === null) {
                $('.next').hide()
            } else if (data.next) {
                $('.next').show()
            }
        }
        // custom ordering
        // search more options
        // allow only get

        // can change type of graph
        $("a.previous").attr("href", data.previous);
        $("a.next").attr("href", data.next);
        $('.content').append(data.count)
    });
}


//$('#content').on('click', '#w', function() {
//    $.ajax({
////        url: your_url,
//        method: 'POST', // or another (GET), whatever you need
//        data: {
//            name: 'xx', // data you need to pass to your function
//            click: True
//        }
//        success: function (data) {
//            // success callback
//            // you can process data returned by function from views.py
//        }
//    });
//});



$("a.next, a.previous").on('click', function() {
    getResults(this.href);
    return false;
})



$('#inputBox').keypress(function(e) {
    if (e.which == 13) {
    getResults();
    //    return false;
    }
})

var thread = null;
$('#inputBox').keyup(function() {
    clearTimeout(thread);
    var $this = $(this);
    thread = setTimeout(function() {
    getResults()
    }, 0);
});



var $loading = $('#loader').hide();
$(document)
  .ajaxStart(function () {
    $loading.show();
  })
  .ajaxStop(function () {
    $loading.hide();
  });