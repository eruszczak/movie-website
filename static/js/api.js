$.fn.api.settings.api = {
    // 'recommend title': '/api/title/{pk}/recommend/',
};

$('.regular.rating').rating({
    initialRating: 0,
    maxRating: 10,
    clearable: true,
    onRate: function (rating) {
        var url = rating === 0 ? $(this).data('remove-url') : $(this).data('url');
        ajax_request({'rating': rating}, {url: url});
    }
});

$('.ui.search').search({
    minCharacters: 3,
    maxResults: 15,
    apiSettings: {
        onResponse: function (serverResponse) {
            var results = [];
            $.each(serverResponse.titles, function(index, item) {
                results.push({
                    title: item.name,
                    description: item.year + ' ' + item.type,
                    url: item.url,
                    image: item.img
                });
            });
            $.each(serverResponse.persons, function(index, item) {
                results.push({
                    title: item.name,
                    description: 'Person',
                    url: item.url,
                    image: item.img
                });
            });
            var action = null;
            if (serverResponse.titles.length) {
                action = {
                    text: 'See more titles',
                    url: serverResponse.action.url
                }
            }
            return {
                results: results,
                action: action
            };
        }
    }
});

var API_SETTINGS_BASE = {
    method : 'POST',
    data: {
      csrfmiddlewaretoken: TOKEN
    },
    onError: function(errorMessage, element, xhr) {
        showErrorToastOrRedirectToLoginWithNext(xhr);
    }
};

const TOGGLE_API_SETTINGS_BASE = $.extend({
    onSuccess: function(response) {
        showToast(response.message);
        if ($(this).hasClass('icon')) {
            // TOGGLE ICON
            if (response.created) {
                $(this).removeClass('empty remove').addClass('active');
            } else {
                $(this).addClass('empty remove').removeClass('active');
            }
        } else if ($(this).hasClass('button')) {
            // TOGGLE BUTTON
            if (response.created) {
                $(this).addClass('positive').text($(this).data('active'));
                console.log($(this).data('active'))
            } else {
                $(this).removeClass('positive').text($(this).data('inactive'));
                console.log($(this).data('inactive'))
            }
        }

    }
}, API_SETTINGS_BASE);

const TOGGLE_FAV = $.extend({action: 'favourite title'}, TOGGLE_API_SETTINGS_BASE);
const TOGGLE_WATCH = $.extend({action: 'watchlist title'}, TOGGLE_API_SETTINGS_BASE);
const TOGGLE_FOLLOW = $.extend({action: 'follow user'}, TOGGLE_API_SETTINGS_BASE);
const TOGGLE_WATCHING = $.extend({action: 'currently watching'}, TOGGLE_API_SETTINGS_BASE);

$('.title-fav').api(TOGGLE_FAV);
$('.title-watch').api(TOGGLE_WATCH);
$('.follow.button').api(TOGGLE_FOLLOW).state({
    text: {
        inactive: 'Follow',
        active: 'Followed'
    }
});
$('.currently-watching.button').api(TOGGLE_WATCHING).state({
    text: {
        inactive: 'Not watching currently',
        active: 'Currently watching'
    }
});

const SHOW_RESULT_MODAL_BASE = $.extend({
    onSuccess: function(response) {
        setModalContentAndShow($('.second.modal'), response);
    }
}, API_SETTINGS_BASE);

var EXPORT_SETTINGS = $.extend({action: 'export ratings'}, SHOW_RESULT_MODAL_BASE);
var CLEAR_SETTINGS = $.extend({action: 'clear ratings'}, SHOW_RESULT_MODAL_BASE);
// $('.recommend.button').api(recommendSettings);
$('.export.modal .actions .positive').api(EXPORT_SETTINGS);
$('.clear.modal .actions .negative').api(CLEAR_SETTINGS);


// var recommendSettings = $.extend({
//     action: 'recommend title',
//     beforeSend: function(settings) {
//         settings.data.recommended_user_ids = $('[name="recommended_user_ids"]').val().split(',');
//         return settings;
//     },
//     onSuccess: function(response) {
//         showToast(response.message);
//         // $('[name="recommended_user_ids"]').val('');
//     }
// }, API_SETTINGS_BASE);