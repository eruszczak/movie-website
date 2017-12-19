

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



// console.log($('[type="tooltip"]'));
$('[type="tooltip"]').popup();
// $('body').on('[type="tooltip"]').popup();
$('.ui.checkbox').checkbox();

// $('body').on('change', '[type="tooltip"]', function() {
//     //Your code
//     console.log('year')
//     console.log($(this))
//     $(this).popup();
//     // $('[type="tooltip"]').popup();
// });

// $('body').on('load', '[type="tooltip"]', function() {
//     $('[type="tooltip"]').popup();
// });

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
$('.ui.dropdown, .dropdown.item').dropdown();
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


$('.ui.accordion')
  .accordion()
;
