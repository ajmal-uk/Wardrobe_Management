from django.shortcuts import render, redirect
from wardrobe.models import Occasion, Season
from .models import OutfitRecommendation
from .utils import generate_outfit_recommendations
from accounts.decorators import role_required
from .utils import generate_outfit_recommendations, calculate_match_score


@role_required('user')
def recommend_outfit(request):

    if request.method == 'POST':
        generate_outfit_recommendations(
            user=request.user,
            occasion_id=request.POST.get('occasion'),
            season_id=request.POST.get('season')
        )
        return redirect('recommend_outfit')

    recommendations = OutfitRecommendation.objects.filter(
        user=request.user
    )

    # 🔹 FORCE SAME SCORE FOR SAME COMBO
    for rec in recommendations:
        correct_score = calculate_match_score(
            rec.top_item,
            rec.bottom_item
        )
        if rec.match_score != correct_score:
            rec.match_score = correct_score
            rec.save(update_fields=['match_score'])

    recommendations = recommendations.order_by('-match_score')

    return render(request, 'user/recommend.html', {
        'recommendations': recommendations,
        'occasions': Occasion.objects.all(),
        'seasons': Season.objects.all(),
    })
