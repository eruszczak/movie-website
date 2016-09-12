$('#go_search').on('click', function() {
    getResults();
});

//function redirect_to_first_page() {
//    redirect_to_first_page = function(){}
//}

function per_page() {
    var page_size = $("#select_per_page option:selected").text()//.toString();
    if (page_size) {
        getResults(null, page_size)
    }
}

function getResults(new_link = null, selected_per_page = false) {
    if (new_link === null) {
        link = '/api/?'
        //    $(".search_content").empty(); // link += '&callback=?';
        //    document.getElementsByName("title")[0].value = '';  //    document.getElementsByName("year")[0].value = '';
        title = document.getElementsByName("q")[0].value;
//        year = document.getElementsByName("year")[0].value;
        if (/*!year && */!title) { return }
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
    $(".search_content").empty();
    var get_page = /(?:\?page=)(\d+)/.exec(link)
    if (get_page) { get_page = get_page[1] - 1 } else { get_page = 0 }

    var get_page_size = /(?:per_page=)(\d+)/.exec(link)
    if (get_page_size) { get_page_size = get_page_size[1] } else { get_page_size = 20 }

    $.getJSON(link, {
//      format: "json"
    }).done(function(data) {
        $.each(data.results, function(count, item) {
//            console.log(get_page, get_page_size, get_page*get_page_size, count)
            var counter = get_page * get_page_size + count + 1
            var link = ' <a href="' + item.detail + '">' + item.name + '</a>'
//            if (item.watch_again_date) {
//                var btn = '<button type="button" class="test_put2 btn btn-sm see-again-btn unwatch-btn">dont want to see again</button>'
//            } else {
//                var btn = '<buttontype="button" class="test_put2 btn btn-sm see-again-btn watch-btn">want to see again</button>'
//            }
            $('.search_content').append(counter, link + '<br>')
        });
        pagination(data)
        // custom ordering
        // search more options

        $('.search_content').append(data.count, ' results')
    });
}


function get_api_data(link) {
    var get_page = /(?:\?page=)(\d+)/.exec(link)
    if (get_page) { get_page = get_page[1] - 1 } else { get_page = 0 }

    var get_page_size = /(?:per_page=)(\d+)/.exec(link)
    if (get_page_size) { get_page_size = get_page_size[1] } else { get_page_size = 20 }

    $.getJSON(link, {
//      format: "json"
    }).done(function(data) {
        x = data
    })
    return x
}


function pagination(data) {
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
    $("a.previous").attr("href", data.previous);
    $("a.next").attr("href", data.next);
}

$("a.next, a.previous").on('click', function() {
    getResults(this.href);
    return false;
})



$('#inputBox_search, #inputBox_watchlist').keypress(function(e) {
    if (e.which == 13) {
        getResults();
        return false;
    }
})

var thread = null;
$('#inputBox_search, #inputBox_watchlist').keyup(function() {
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
