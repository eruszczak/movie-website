$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover()

    $("#recommend_form").submit(function(event) {
        var const_value = $("#id_const").val();
        var valid_note = $("#id_note").val().length < 120;
        var nick_field = $("#id_nick");
        var regex = /(tt\d{7})[^\d]*/;
        var valid_const = regex.exec(const_value)[1];

        if (valid_const && valid_note) {
            $("#id_const").val(valid_const);
            if (!nick_field.length || (nick_field.val().length > 2)) {
                return true;
            }
        }
        return false;
    });

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

    if ($('div').is('#favouritePage')) {
        var pathArray = window.location.pathname.split('/');
        var path_username = pathArray[pathArray.length - 3];
        if (path_username == request_username) {
            sortable();
        }
    }

    $('input.filter_results').on('change', function() {
       $('input.filter_results').not(this).prop('checked', false);
    });

    // when on title page you click 1 of 10 stars
    $('input[name="rating"').change(function() {
        ajax_request({'value': this.value}, true);
    });

    // now it's not needed because order is saved without button click
//    $('#save-order').click(function() {
//        var ordering = $('#sortable').sortable('serialize');
//        ajax_request({'item_order': ordering}, true);
//    });
});

function sortable() {
    $('#sortable').sortable({
        placeholder: 'sort-placeholder',
        axis: 'y',
        update: function (event, ui) {
//            $('#save-order').removeClass('disabled');
            var ordering = $(this).sortable('serialize');
            $(this).find('li').each(function(i){
                $(this).find('p.item-order').text(i+1);
            });
            ajax_request({'item_order': ordering});
        }
    });
    $("#sortable").disableSelection();
}

function ajax_request(data, refresh = false, destination = this.href) {
    data['csrfmiddlewaretoken'] = csrftoken;
    $.ajax({
        data: data,
        type: 'POST',
        url: destination
    });
    if (refresh) {
        window.location.reload(false);
    }
}

var csrftoken = getCookie('csrftoken');
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
