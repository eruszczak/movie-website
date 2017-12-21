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

$('.export.tiny.modal').modal('attach events', '.export-ratings.button', 'show');
$('.import.tiny.modal').modal('attach events', '.import-ratings.button', 'show');
