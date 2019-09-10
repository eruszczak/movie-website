from django.forms.widgets import SelectMultiple, ClearableFileInput, NumberInput, DateInput


class MySelectMultipleWidget(SelectMultiple):
    template_name = 'shared/widgets/select.html'
    # option_template_name = 'widgets/select_option.html'


class MyClearableFileInput(ClearableFileInput):
    template_name = 'shared/widgets/clearable_file_input.html'


class MyRatingWidget(NumberInput):
    """widget that renders hidden input and star rating. Clicking on rating will set input's value"""
    template_name = 'shared/widgets/rating.html'


class MyDateWidget(DateInput):
    """widget that renders hidden input and star rating. Clicking on rating will set input's value"""
    template_name = 'shared/widgets/date.html'
