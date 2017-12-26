$('[type="tooltip"]').popup();
$('.ui.checkbox').checkbox();

$('.tabular.menu .item').tab();
$('.ui.menu').tab();
$('.ui.dropdown, .dropdown.item').dropdown();

$('.title-menu .item').tab();
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


$('.ui.accordion').accordion();

$('.clear.tiny.modal').modal('attach events', '.clear-ratings.button', 'show');
$('.export.tiny.modal').modal('attach events', '.export-ratings.button', 'show');
$('.watchlist.tiny.modal').modal('attach events', '.update-watchlist.button', 'show');
$('.ratings.tiny.modal').modal('attach events', '.update-ratings.button', 'show');
$('.import.tiny.modal').modal({
    onApprove: function (e) {
        $('#import-form').submit();
    }
}).modal('attach events', '.import-ratings.button', 'show');
