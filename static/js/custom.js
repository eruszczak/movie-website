$('[type="tooltip"]').popup();
$('.ui.checkbox').checkbox();

$('.tabular.menu .item').tab();
$('.ui.menu').tab();
$('.ui.dropdown, .dropdown.item').dropdown();

$('.title-menu .item').tab();
$('.ui.embed').embed();
$('.tiny.modal').modal('show');


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
