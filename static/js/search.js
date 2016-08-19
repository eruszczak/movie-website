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
    $(".content").empty();
    var get_page = /(?:\?page=)(\d+)/.exec(link)
    if (get_page) { get_page = get_page[1] - 1 } else { get_page = 0 }

    var get_page_size = /(?:per_page=)(\d+)/.exec(link)
    if (get_page_size) { get_page_size = get_page_size[1] } else { get_page_size = 20 }

    $.getJSON(link, {
//      format: "json"
    }).done(function(data) {
        $.each(data.results, function(count, item) {
//            console.log(get_page, get_page_size, get_page*get_page_size, count)
            $('.content').append(get_page * get_page_size + count + 1, item.name + '<br>')
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
        // get page size so user can chagne it ?per_page=10
        // custom ordering
        // search more options
        // allow only get
        $("a.previous").attr("href", data.previous);
        $("a.next").attr("href", data.next);
        $('.content').append(data.count)
    });
}



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