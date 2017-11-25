from django.forms.widgets import SelectMultiple


class MySelectMultipleWidget(SelectMultiple):
    template_name = 'shared/widgets/select.html'
    # option_template_name = 'widgets/select_option.html'
