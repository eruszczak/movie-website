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

    $('[name="update_titles_form"').children().on('click', function() {
        showWaitingDialog(60);
    });

    $("#import_ratings").on('click', function(e) {
        e.preventDefault();
        $("#import").trigger('click');
    });

    if ( $( "#import").length ) {
        document.getElementById("import").onchange = function() {
            var max_size = 2 * 1024 * 1024;
            if(max_size < document.getElementById("import").files[0].size) {
                alert('File is too big. Max 2MB.');
                return;
            }
            document.getElementById("import_form").submit();
            showWaitingDialog(60);
        };
    }

    var selectors = 'button[name="fav"], button[name="unfav"], button[name="watch"], button[name="unwatch"]';
    $('body').on('click', selectors, function() {
        var data = {'const': $(this).val()};
        var btnName = $(this).attr('name');
        data[btnName] = btnName;
        ajax_request(data, {url: '/explore/'});

        var btn = buttons[btnName];
        $(this).removeClass(btn.class).addClass(btn.afterClass);
        $(this).attr('name', btn.afterName);
        var span = $(this).find('span').attr('class', btn.afterSpanClass);
        $(this).html(span);
        $(this).append(' ' + btn.afterText);
    });


    if ($('table').is('#sortable')) {
        var pathArray = window.location.pathname.split('/');
        var path_username = pathArray[pathArray.length - 3];
        if (path_username == request_username) {
            sortable();
        }
    }

    $('.raty-stars').raty({
        path: function() {
            return this.getAttribute('data-path');
        },
        score: function() {
            return $(this).attr('data-score');
        },
        click: function(score, evt) {
            score = score || 0;
            var data = {
                'const': this.id,
                'rating': score
            }
            $(this).parent().find('[name="rating"]').val(score);
            var sourcePage = $(this).attr('data-source');

            if (sourcePage == 'details_page') {
                $(this).parent().submit();
            } else {
                ajax_request(data, {url: '/explore/'});
            }

        },

        number: 10,
        cancel: function() {
            console.log($(this).attr('data-score'));
            return $(this).attr('data-score');
        },
        cancelHint: '',

        target: function() {
            return '#descr-' + this.id;
        },
        targetType: 'score',
        targetKeep: true
    });

    $('input.filter_results').on('change', function() {
       $('input.filter_results').not(this).prop('checked', false);
    });

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
        if (this.checked) {
            previousRatings = $('#previewRatings').val();
            $('#previewRatings').val('');
        } else {
            $('#previewRatings').val(previousRatings);
        }
    });
    $('#picture-clear_id').change(function() {
        if (this.checked) {
            previousAvatar = $('#previewAvatar').val();
            $('#previewAvatar').val('');
        } else {
            $('#previewAvatar').val(previousAvatar);
        }
    });

    var elems = $('#search_form_checkboxes').children();
    $('#selectCompareWithUser').on('change', function() {
        if(this.value) {
            elems.show();
        } else {
            elems.hide();
        }
    });

    var selectedUser = $('#selectCompareWithUser').val();
    if(selectedUser) {
        if(selectedUser.length)
            elems.show();
    }


    $("#btnSubmit").attr("disabled", "disabled");
    $('#id_username, #id_password').keyup(function() {
        var validated = false;
        var username = $('#id_username').val();
        var password = $('#id_password').val();

        if (username.length && password.length) {
            validated = true;
        }

        if (validated) {
            $("#btnSubmit").removeAttr("disabled");
        } else {
            $("#btnSubmit").attr("disabled", "disabled");
        }
    });
});

function sortable() {
    $('#sortable tbody').sortable({
        placeholder: 'ui-state-highlight',
        axis: 'y',
        update: function (event, ui) {
            var item = ui.item.find('.item-order');
            var itemId = item.parent().parent().attr('id');
            var ordering = $(this).sortable('serialize');
            var o = $(this).sortable('toArray');

            $(this).find('tr').each(function(i) {
                var order = $(this).find('.item-order');
                var orderChange = order.next();
                order.hide();
                if (itemId == this.id) {
                    var newOrder = o.indexOf(itemId) + 1;
                    var previousOrder = parseInt(item.text());
                    var orderDiff = newOrder - previousOrder;
                    var txt = (orderDiff > 0 ? '+' : '') + orderDiff;
                    order.text(newOrder);
                    orderChange.text(txt);
                    orderChange.attr('class', 'order-change');
                    if (orderDiff > 0) {
                        orderChange.addClass('green-color');
                    } else {
                        orderChange.addClass('red-color');
                    }
                } else {
                    order.text(i + 1);
                    orderChange.text('');
                    orderChange.attr('class', 'order-change');

                }
                order.fadeIn('slow');
            });
            ajax_request({'item_order': ordering});
        }
    });
    $("#sortable").disableSelection();
}

function ajax_request(data, options) {
    data.csrfmiddlewaretoken = csrftoken;
    var sourceUrl = [location.protocol, '//', location.host, location.pathname].join('');

    options = options || {};
    var refresh = options.refresh || false;
    var url = options.url || sourceUrl;
    console.log(data)

    $.ajax({
        data: data,
        type: 'POST',
        url: url,
        success: function() {
            if (refresh) {
                window.location.reload(false);
            }
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
$('.selectpicker').selectpicker({});

function showWaitingDialog(secs) {
    waitingDialog.show();
    setTimeout(function () {
        waitingDialog.hide();
    }, secs * 1000);
}