const TOKEN = getCookie('csrftoken');

const API_SETTINGS_BASE = {
    method: 'POST',
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
            } else {
                $(this).removeClass('positive').text($(this).data('inactive'));
            }
        }
    }
}, API_SETTINGS_BASE);

const SHOW_RESULT_MODAL_BASE = $.extend({
    onSuccess: function(response) {
        setModalContentAndShow($('.second.modal'), response);
    }
}, API_SETTINGS_BASE);

$('.title-fav, .title-watch, .follow.button, .currently-watching.button, .title-update').api(TOGGLE_API_SETTINGS_BASE);
$('.export.modal .actions .positive, .clear.modal .actions .negative').api(SHOW_RESULT_MODAL_BASE);

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
                    title: item.name + ' (' + item.year + ' ' + item.type + ')',
                    // description: item.year + ' ' + item.type,
                    url: item.url,
                    // image: item.img
                });
            });
            $.each(serverResponse.persons, function(index, item) {
                results.push({
                    title: item.name,
                    // description: 'Person',
                    url: item.url,
                    // image: item.img
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