from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RecommendForm
from .models import Recommendation
from datetime import date


def recommend(request, username):
    user = User.objects.get(username=username)
    recommended_for_user = Recommendation.objects.filter(user=user)
    if request.method == 'POST':
        if request.POST.get('delete_recommend'):
            to_del = Recommendation.objects.filter(pk=request.POST.get('recommend_pk'), user=request.user).first()
            if to_del.is_active:
                messages.info(request, 'Deleted <a href="{}">{}</a> from recommendations'.format(
                    to_del.title.get_absolute_url(), to_del.title.name), extra_tags='safe')
                to_del.delete()
            return redirect(user.userprofile.recommend_url())

        form = RecommendForm(request.POST, request=request, user=user, recommendations=recommended_for_user)
        if form.is_valid():
            # i cant use form because not every field is there
            instance = Recommendation(user=user)
            instance.title = form.cleaned_data.get('const')
            instance.note = form.cleaned_data.get('note')
            user, is_logged = form.cleaned_data.get('nick')
            if is_logged:
                instance.sender = user
            else:
                instance.nick = user
            instance.save()
            messages.success(request, 'Added recommendation')
            return redirect(user.userprofile.recommend_url())
    else:
        form = RecommendForm()

    recommended_for_user = recommended_for_user.extra(select={
        'days_diff': """
            SELECT "movie_rating"."rate_date" - "recommend_recommendation"."added_date"::timestamp::date
            FROM "movie_rating"
            WHERE (
                "movie_rating"."user_id" = %s
                AND "movie_rating"."rate_date" >= "recommend_recommendation"."added_date"::timestamp::date
                AND "movie_rating"."title_id" = "recommend_recommendation"."title_id"
            )
            ORDER BY "movie_rating"."rate_date" ASC LIMIT 1
        """,
        'req_user_curr_rating': """
            SELECT "movie_rating"."rate"
            FROM "movie_rating"
            WHERE (
                "movie_rating"."user_id" = %s
                AND "movie_rating"."rate_date" >= "recommend_recommendation"."added_date"::timestamp::date
                AND "movie_rating"."title_id" = "recommend_recommendation"."title_id"
            )
            ORDER BY "movie_rating"."rate_date" DESC LIMIT 1
        """,
        'user_curr_rating': """
        SELECT "movie_rating"."rate"
        FROM "movie_rating"
        WHERE (
            "movie_rating"."user_id" = %s
            AND "movie_rating"."rate_date" >= "recommend_recommendation"."added_date"::timestamp::date
            AND "movie_rating"."title_id" = "recommend_recommendation"."title_id"
        )
        ORDER BY "movie_rating"."rate_date" ASC LIMIT 1
    """
        }, select_params=[request.user.id, request.user.id, user.id])

    context = {
        'obj_list': recommended_for_user,
        'form': form,
        'count': {
            'today': recommended_for_user.filter(added_date__date=date.today()).count(),
            'active_recommendations': sum(1 for r in recommended_for_user if r.days_diff is None),
        },
        'is_owner': user == request.user,
        'title': 'recommended for ' + user.username,
        'choosen_user': user
    }
    return render(request, 'recommend.html', context)
