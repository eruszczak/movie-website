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
        showWaitingDialog(100);
    });

    $("#import_ratings").on('click', function(e) {
        e.preventDefault();
        $("#import").trigger('click');
    });

    $("#clear_ratings").on('click', function(e) {
      e.preventDefault();
        $( "#dialog-confirm" ).dialog({
          resizable: false,
          height: "auto",
          width: 400,
          modal: true,
          buttons: {
            "Clear my ratings": function() {
              $( this ).dialog( "close" );
              nickname = $('#confirm-nickname').val();
              var formElement = $("#confirm-nick");
              formElement.val(nickname);
              formElement.parent().submit();
            },
            Cancel: function() {
              $( this ).dialog( "close" );
            }
          }
        });
    });

    if ($( "#import").length) {
        document.getElementById("import").onchange = function() {
            var max_size = 2 * 1024 * 1024;
            if(max_size < document.getElementById("import").files[0].size) {
                showToast('File is too big. Max 2MB.');
                return;
            }
            document.getElementById("import_form").submit();
            showWaitingDialog(100);
        };
    }
    var selectors = 'button[name="fav"], button[name="unfav"], button[name="watch"], button[name="unwatch"], button[name="follow"], button[name="unfollow"]';
    $('body').on('click', selectors, function() {
        var btnValue = $(this).val();
        var btnName = $(this).attr('name');
        var data = {'const': btnValue};
        data[btnName] = btnName;
        var viewUrl = '/explore/';
        if (btnName === 'follow' || btnName === 'unfollow') {
            viewUrl = '/users/' + btnValue + '/';
        }
        ajax_request(data, {url: viewUrl});

        // toggle button look
        $(this).hide();
        var btn = buttons[btnName];
        showToast(btn.toastMessage);
        $(this).removeClass(btn.class).addClass(btn.afterClass);
        $(this).attr('name', btn.afterName);
        var span = $(this).find('span').attr('class', btn.afterSpanClass);
        $(this).html(span);
        $(this).append(' ' + btn.afterText);
        $(this).fadeIn();
    });

    if ($('table').is('#sortable')) {
        var isOwner = $('#sortable').data('isowner');
        if (isOwner) {
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
                if (score === 0) {
                    showToast('Rating deleted.');
                } else {
                    showToast('Created new rating.');
                }
                ajax_request(data, {url: '/explore/'});
            }

        },

        number: 10,
        cancel: function() {
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

    $(".dropdown").hover(
        function() {
            $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true, true).slideDown("400");
            $(this).toggleClass('open');
        },
        function() {
            $('.dropdown-menu', this).not('.in .dropdown-menu').stop(true, true).slideUp("400");
            $(this).toggleClass('open');
        }
    );
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
                orderChange.hide();
                if (itemId == this.id) {
                    var newOrder = o.indexOf(itemId) + 1;
                    var previousOrder = parseInt(item.text());
                    var orderDiff = previousOrder - newOrder;
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
                orderChange.fadeIn('slow');
            });
            showToast('Saved new order.');
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
        'afterSpanClass': 'glyphicon glyphicon-heart-empty',
        'toastMessage': 'Added to favourites'
    },
    'unfav': {
        'class': 'unwatch-btn',
        'afterClass': 'watch-btn',
        'afterName': 'fav',
        'afterText': '',
        'afterSpanClass': 'glyphicon glyphicon-heart',
        'toastMessage': 'Removed from favourites'
    },
    'watch': {
        'class': 'watch-btn',
        'afterClass': 'unwatch-btn',
        'afterName': 'unwatch',
        'afterText': 'watchlist',
        'toastMessage': 'Added to watchlist'
    },
    'unwatch': {
        'class': 'unwatch-btn',
        'afterClass': 'watch-btn',
        'afterName': 'watch',
        'afterText': 'add to watchlist',
        'toastMessage': 'Removed from watchlist'
    },
    'follow': {
        'class': 'watch-btn',
        'afterClass': 'unwatch-btn',
        'afterName': 'unfollow',
        'afterText': 'Unfollow',
        'afterSpanClass': 'glyphicon glyphicon-eye-close',
        'toastMessage': 'Followed user'
    },
    'unfollow': {
        'class': 'unwatch-btn',
        'afterClass': 'watch-btn',
        'afterName': 'follow',
        'afterText': 'Follow',
        'afterSpanClass': 'glyphicon glyphicon-eye-open',
        'toastMessage': 'Unfollowed user'
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

function showToast(message) {
    $.iaoAlert({
        msg: message,
        type: "notification",
        alertTime: "1750",
        position: 'top-right',
        mode: 'dark',
        fadeOnHover: true,
    })
}