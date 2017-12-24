from django.forms.widgets import SelectMultiple, ClearableFileInput


class MySelectMultipleWidget(SelectMultiple):
    template_name = 'shared/widgets/select.html'
    # option_template_name = 'widgets/select_option.html'


class MyClearableFileInput(ClearableFileInput):
    template_name = 'shared/widgets/clearable_file_input.html'
