$.fn.api.settings.api = {
    'search': '/api/search?keyword={query}',
    'follow user': '/api/user/{pk}/follow',
    'favourite title': '/api/title/{pk}/favourites',
    'watchlist title': '/api/title/{pk}/watchlist',
    'recommend title': '/api/title/{pk}/recommend',
    'currently watching': '/api/{pk_user}/{pk_title}/watch'
};

$('.rating').rating({
    initialRating: 0,
    maxRating: 10,
    clearable:true,
    onRate: function (rating) {
        var data = {
            'rating': rating,
            'insert_as_new': false
        };
        ajax_request(data, {url: $(this).data('url')});
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
                    description: 'Actor',
                    url: item.url,
                    image: item.img
                });
            });
            var action = null;
            if (serverResponse.titles.length) {
                var action = {
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

var titleFavSettings = $.extend(true, {
    action: 'favourite title',
    beforeSend: function(settings) {
      settings.data.rating = $(this).hasClass('active') ? 0: 1;
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
        $(this).toggleClass('empty').toggleClass('active');
    }
}, API_SETTINGS_BASE);

var titleWatchSetttings = $.extend(true, {
    action: 'watchlist title',
    beforeSend: function(settings) {
      settings.data.rating = $(this).hasClass('active') ? 0: 1;
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
        $(this).toggleClass('remove').toggleClass('active');
    }
}, API_SETTINGS_BASE);

var recommendSettings = $.extend(true, {
    action: 'recommend title',
    beforeSend: function(settings) {
      settings.data.recommended_user_ids = $('[name="recommended_user_ids"]').val().split(',');
      // var fieldName = $(this).data('field-name');
      // settings.data[fieldName] = $('#' + fieldName).val();
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
        // $('[name="recommended_user_ids"]').val('');
    }
}, API_SETTINGS_BASE);

var followSettings = $.extend(true, {
    action: 'follow user',
    beforeSend: function(settings) {
      settings.data.rating = $(this).hasClass('active') ? 0: 1;
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
    }
}, API_SETTINGS_BASE);

var currentlyWatchingSettings = $.extend(true, {
    action: 'currently watching',
    beforeSend: function(settings) {
      settings.data.rating = $(this).hasClass('active') ? 0: 1;
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
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
$('.currently-watching.button').api(currentlyWatchingSettings);