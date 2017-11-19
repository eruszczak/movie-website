

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

$('.ui.dropdown').dropdown();

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

// var $toggle  = $('.ui.toggle.button');
// $toggle
// .state({
//   text: {
//     inactive : 'Vote',
//     active   : 'Voted'
//   }
// })
// ;


// $('.test .menu .item')
$('.user-menu .item')//.not('.active')
  .tab({
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
  });

$('.user-menu .item').first().click();
// $('.user-menu .item.active')
//   .tab()
// ;

$('.user-list-popup')
  .popup({
    inline     : true,
    hoverable  : true,
    // position   : 'bottom left',
    // delay: {
    //   show: 300,
    //   hide: 800
    // }
  })
;

$('.ui.embed').embed();

// $('')
//   .search({
//     apiSettings: {
//       url: ''
//     },
//     fields: {
//       results : 'items',
//       title   : 'name',
//       url     : 'html_url'
//     },
//     minCharacters : 3
//   })
// ;