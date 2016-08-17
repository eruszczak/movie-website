$('#go').on('click', function() {
    getResults();
});

function getResults(new_link=null) {
    if (new_link === null) {
        link = 'http://127.0.0.1:8000/api/?'
        //    $(".content").empty();
        // link += '&callback=?';
        title = document.getElementsByName("q")[0].value;
        year = document.getElementsByName("year")[0].value;
        //    document.getElementsByName("title")[0].value = '';
        //    document.getElementsByName("year")[0].value = '';
        if (!year && !title) {
            return;
        }
        if (title) {
            link += 'q=' + title;
        }
    } else {
        link = new_link
    }
    call_api(link);

}

function call_api(link) {
    $(".content").empty();
    $.getJSON(link, {
//      format: "json"
    }).done(function(data) {
        $.each(data.results, function(count, item) {
            $('.content').append(item.name + '<br>')
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
        var get_page = /(?:page=)(\d+)/.exec(link)
        if (get_page) {
            console.log(get_page[1])
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