

// $('.toggle-fav, .toggle-watch, .toggle-follow').click(function() {
//     var name = $(this).attr('name');
//     var data = {};
//     data[name] = true;
//     var that = this;
//     ajax_request(data, {url: $(this).data('url')}, function() {
//         $(that).siblings().css('display', '');
//         $(that).hide();
//     });
// });

// $('.ui.dropdown').dropdown();

$('.rating').rating({
    initialRating: 0,
    maxRating: 10,
    clearable:true,
    onRate: function (rating) {
        console.log(rating);
        var data = {
            'rating': rating,
            'insert_as_new': false
        };
        ajax_request(data, {url: $(this).data('url')});
    }
});

$('[type="tooltip"]').popup();
$('.ui.checkbox').checkbox();

// var $toggle  = $('.ui.toggle.button');
// $toggle
// .state({
//   text: {
//     inactive : 'Vote',
//     active   : 'Voted'
//   }
// })
// ;


$('.tabular.menu .item').tab();
$('.ui.menu').tab();
$('.dropdown.item').dropdown();
// $('.ui.dropdown')
//   .dropdown()
// ;

// $('.test .menu .item')
$('.title-menu .item').tab();
// $('.user-menu .item')//.not('.active')
//   .tab({
    // cache: false,
    // // faking API request
    // apiSettings: {
    //   loadingDuration : 300,
    //   mockResponse: function(settings) {
    //     var response = {
    //       first  : 'AJAX Tab One',
    //       second : 'AJAX Tab Two',
    //       third  : 'AJAX Tab Three'
    //     };
    //     return response[settings.urlData.tab];
    //   }
    // },
    // context : 'parent',
    // auto    : true,
    // // path    : '/'
  // });

// $('.user-menu .item.active').click();
// $('.user-menu .item.active')
//   .tab()
// ;

// $('.user-list-popup')
//   .popup({
//     inline     : true,
//     hoverable  : true,
//     // position   : 'bottom left',
//     // delay: {
//     //   show: 300,
//     //   hide: 800
//     // }
//   })
// ;

$('.ui.embed').embed();

$('.ui.search').search({
    minCharacters: 3,
    apiSettings: {
        onResponse: function (serverResponse) {
            var results = [];
            $.each(serverResponse.results, function(index, item) {
                // if (index >= 20) {
                //     return false;
                // }
                results.push({
                    title: item.name,
                    description: item.type,
                    url: item.url,
                    image: item.img
                });
            });
            return {
                results: results,
                action: {
                    actionText: 'See more',
                    actionURL: 'http://127.0.0.1:8000/'
                }
            };
        }
    }
});

$('.follow.button').api({
    action: 'follow user',
    method : 'POST',
    data: {
      csrfmiddlewaretoken: TOKEN
    },
    beforeSend: function(settings) {
      settings.data.rating = $(this).hasClass('active') ? 0: 1;
      return settings;
    }
}).state({
    text: {
      inactive: 'Follow',
      active: 'Followed'
    }
});

$('.title-fav').api({
    action: 'favourite title',
    method : 'POST',
    data: {
      csrfmiddlewaretoken: TOKEN
    },
    beforeSend: function(settings) {
      settings.data.rating = $(this).hasClass('active') ? 0: 1;
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
        $(this).toggleClass('empty').toggleClass('active');
    }
});

$('.title-watch').api({
    action: 'watchlist title',
    method : 'POST',
    data: {
      csrfmiddlewaretoken: TOKEN
    },
    beforeSend: function(settings) {
      settings.data.rating = $(this).hasClass('active') ? 0: 1;
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
        $(this).toggleClass('remove').toggleClass('active');
    }
});

$('.recommend.button').api({
    action: 'recommend title',
    method : 'POST',
    data: {
      csrfmiddlewaretoken: TOKEN
    },
    beforeSend: function(settings) {
      settings.data.user_list = $('.recommend.dropdown').find('input').val();
      return settings;
    },
    onSuccess: function(response) {
        showToast(response.message);
    }
});

$('.recommend.dropdown').dropdown({
    onChange: function(value, text, choice) {
        var selectedOptions = value.split(',');
        if (selectedOptions.length > 0 && selectedOptions[0].length > 0) {
            $('.recommend.button').removeClass('hide');
        } else {
            $('.recommend.button').addClass('hide');
        }
    }
});


$('.grid .backdrop-card img').visibility({
    type       : 'image',
    transition : 'fade in',
    duration   : 1000
});