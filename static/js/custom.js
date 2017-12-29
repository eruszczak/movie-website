$('[type="tooltip"]').popup();
$('.ui.checkbox').checkbox();
$('.tabular.menu .item').tab();
$('.ui.menu').tab();
$('.ui.dropdown, .dropdown.item').dropdown();
$('.ui.embed').embed();
$('.ui.accordion').accordion();

$('.title-menu .item').tab({
    onVisible: function(tabPath, parameterArray, historyEvent) {
        $('.slick-carousel-small').slick('setPosition');
    }
});

// every image  I want to lazy load is rendered with `data-src` and `type="src"`
$('[type="src"]').visibility({
    type: 'image',
    transition: 'fade in',
    duration: 500
});

$('.clear.tiny.modal').modal('attach events', '.clear-ratings.button', 'show');
$('.export.tiny.modal').modal('attach events', '.export-ratings.button', 'show');
$('.watchlist.tiny.modal').modal('attach events', '.update-watchlist.button', 'show');
$('.ratings.tiny.modal').modal('attach events', '.update-ratings.button', 'show');
$('.import.tiny.modal').modal({
    onApprove: function (e) {
        $('#import-form').submit();
    }
}).modal('attach events', '.import-ratings.button', 'show');

$(document).ready(function(){
    $('.right.menu.open').on("click",function(e){
        e.preventDefault();
        $('.ui.vertical.menu').toggle();
    });
    
    $('.ui.dropdown').dropdown();
});