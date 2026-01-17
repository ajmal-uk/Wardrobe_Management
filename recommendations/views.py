from django.shortcuts import render, redirect
from wardrobe.models import Occasion, Season
from .models import OutfitRecommendation
from .utils import generate_outfit_recommendations
from accounts.decorators import role_required
from .utils import generate_outfit_recommendations, calculate_match_score


role_required('user')
def recommend_outfit(request):

    selected_occasion = None
    selected_season = None

    if request.method == 'POST':
        selected_occasion = request.POST.get('occasion') or None
        selected_season = request.POST.get('season') or None

        generate_outfit_recommendations(
            user=request.user,
            occasion_id=selected_occasion,
            season_id=selected_season
        )

        request.session['occasion'] = selected_occasion
        request.session['season'] = selected_season

        return redirect('recommend_outfit')

    # 🔹 Read last selection
    selected_occasion = request.session.get('occasion')
    selected_season = request.session.get('season')

    recommendations = OutfitRecommendation.objects.filter(user=request.user)

    if selected_occasion:
        recommendations = recommendations.filter(
            top_item__occasion_id=selected_occasion,
            bottom_item__occasion_id=selected_occasion
        )

    if selected_season:
        recommendations = recommendations.filter(
            top_item__season_id=selected_season,
            bottom_item__season_id=selected_season
        )

    # 🔹 Ensure score consistency
    for rec in recommendations:
        correct_score = calculate_match_score(rec.top_item, rec.bottom_item)
        if rec.match_score != correct_score:
            rec.match_score = correct_score
            rec.save(update_fields=['match_score'])

    recommendations = recommendations.order_by('-match_score')

    return render(request, 'user/recommend.html', {
        'recommendations': recommendations,
        'occasions': Occasion.objects.all(),
        'seasons': Season.objects.all(),
    })

