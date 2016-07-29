from django import forms


class ChartForm(forms.Form):
    OPTIONS = (
        ("chart_genres", "Genres"),
        ("chart_ratings", "Ratings"),
        ("chart_last_year_ratings", "From last year"),
        ("distribution_by_year", "Year"),
    )
    chart = forms.ChoiceField(choices=OPTIONS)
