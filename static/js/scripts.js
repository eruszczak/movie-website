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

    var selectors = 'button[name="fav"], button[name="unfav"], button[name="watch"], button[name="unwatch"]';
    $('body').on('click', selectors, function() {
        var data = {'const': $(this).val()};
        var btnName = $(this).attr('name');
        data[btnName] = btnName;
        ajax_request(data);

        var btn = buttons[btnName];
        $(this).removeClass(btn.class).addClass(btn.afterClass);
        $(this).attr('name', btn.afterName);
        var span = $(this).find('span').attr('class', btn.afterSpanClass);
        $(this).html(span);
        $(this).append(' ' + btn.afterText);
    });


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
    if ( $( "#star_rating_form" ).length ) {
        $('input[name="rating"').change(function() {
            $("#star_rating_form").submit();
        });
    }

    // when on explore page you click 1 of 10 stars
    if ( $( ".star_rating_form_many" ).length ) {
        $('input[name="rating"').change(function() {
            var titleConst = $(this).parent().prev().val();
            var rating = $(this).val();
            console.log($(this).parent().attr('id'));
            var data = {'const': titleConst, 'rating': rating};
            console.log(data);
//            ajax_request(data);
        });
    }

    $(document).on('change', ':file', function() {
        var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
        input.trigger('fileselect', [numFiles, label]);
    });

    $(':file').on('fileselect', function(event, numFiles, label) {
        var input = $(this).parents('.input-group').find(':text')
        if( input.length ) {
            input.val(label);
        }
    });

    var previousAvatar = '';
    var previousRatings = '';

    $('#csv_ratings-clear_id').change(function() {
//    $(document).on('change', '#csv_ratings-clear_id', function() {
        if (this.checked) {
            previousRatings = $('#previewRatings').val();
            $('#previewRatings').val('');
        } else {
            $('#previewRatings').val(previousRatings);
        }
    });
    $('#picture-clear_id').change(function() {
//    $(document).on('change', '#picture-clear_id', function() {
        if (this.checked) {
            previousAvatar = $('#previewAvatar').val();
            $('#previewAvatar').val('');
        } else {
            $('#previewAvatar').val(previousAvatar);
        }
    });

    $('#selectCompareWithUser').on('change', function() {
        if(this.value) {
            $('#exclude_mine, #exclude_his').show();
        } else {
            $('#exclude_mine, #exclude_his').hide();
        }
    });

    var selectedUser = $('#selectCompareWithUser').val()[0];
    if(selectedUser) {
        $('#exclude_mine, #exclude_his').show();
    }

});

function sortable() {
    $('#sortable').sortable({
        placeholder: 'sort-placeholder',
        axis: 'y',
        update: function (event, ui) {
            var ordering = $(this).sortable('serialize');
            $(this).find('li').each(function(i){
                $(this).find('p#item-order').text(i+1);
            });
            ajax_request({'item_order': ordering});
        }
    });
    $("#sortable").disableSelection();
}

function ajax_request(data, refresh=false) {
    data['csrfmiddlewaretoken'] = csrftoken; // attach csrf token
    var url = [location.protocol, '//', location.host, location.pathname].join('');
    $.ajax({
        data: data,
        type: 'POST',
        url: url,
        success: function() {
//            if (refresh) {
//                window.location.reload(false);
//            }
        }
    });
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

var buttons = {
    'fav': {
        'class': 'watch-btn',
        'afterClass': 'unwatch-btn',
        'afterName': 'unfav',
        'afterText': '',
        'afterSpanClass': 'glyphicon glyphicon-heart-empty'
    },
    'unfav': {
        'class': 'unwatch-btn',
        'afterClass': 'watch-btn',
        'afterName': 'fav',
        'afterText': '',
        'afterSpanClass': 'glyphicon glyphicon-heart'
    },
    'watch': {
        'class': 'watch-btn',
        'afterClass': 'unwatch-btn',
        'afterName': 'unwatch',
        'afterText': 'watchlist',
    },
    'unwatch': {
        'class': 'unwatch-btn',
        'afterClass': 'watch-btn',
        'afterName': 'watch',
        'afterText': 'add to watchlist',
    }
}

// to prevent search form flickering on page load
$('.selectpicker').selectpicker({
});