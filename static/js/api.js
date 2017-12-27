$.fn.api.settings.api = {
    'search': '/api/search/?keyword={query}',
    'follow user': '/api/user/{pk}/follow/',
    'export ratings': '/importer/user/{pk}/export/',
    'favourite title': '/api/title/{pk}/favourites/',
    'watchlist title': '/api/title/{pk}/watchlist/',
    'recommend title': '/api/title/{pk}/recommend/',
    'currently watching': '/api/tv/{pk}/watching/',
    'clear ratings': '/api/clear-ratings/'
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

var titleFavSettings = $.extend({
    action: 'favourite title',
    onSuccess: function(response) {
        showToast(response.message);
        $(this).toggleClass('empty').toggleClass('active');
    }
}, API_SETTINGS_BASE);

var titleWatchSetttings = $.extend({
    action: 'watchlist title',
    onSuccess: function(response) {
        showToast(response.message);
        $(this).toggleClass('remove').toggleClass('active');
    }
}, API_SETTINGS_BASE);

var recommendSettings = $.extend({
    action: 'recommend title',
    beforeSend: function(settings) {
        settings.data.recommended_user_ids = $('[name="recommended_user_ids"]').val().split(',');
        return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
        // $('[name="recommended_user_ids"]').val('');
    }
}, API_SETTINGS_BASE);

var followSettings = $.extend({
    action: 'follow user',
    onSuccess: function(response) {
        showToast(response.message);
    }
}, API_SETTINGS_BASE);

var currentlyWatchingSettings = $.extend({
    action: 'currently watching',
    onSuccess: function(response) {
        showToast(response.message);
    }
}, API_SETTINGS_BASE);

var exportRatingsSettings = $.extend({
    action: 'export ratings',
    onSuccess: function(response) {
        setModalContentAndShow($('.second.modal'), response);
    }
}, API_SETTINGS_BASE);

var clearRatingsSettings = $.extend({
    action: 'clear ratings',
    onSuccess: function(response) {
        setModalContentAndShow($('.second.modal'), response);
    }
}, API_SETTINGS_BASE);


$('.title-fav').api(titleFavSettings);
$('.title-watch').api(titleWatchSetttings);
$('.recommend.button').api(recommendSettings);
$('.follow.button').api(followSettings).state({
    text: {
      inactive: 'Follow',
      active: 'Followed'
    }
});
$('.currently-watching.button').api(currentlyWatchingSettings).state({
    text: {
      inactive: 'Not watching currently',
      active: 'Currently watching'
    }
});
$('.export.modal .actions .positive').api(exportRatingsSettings);
$('.clear.modal .actions .negative').api(clearRatingsSettings);
