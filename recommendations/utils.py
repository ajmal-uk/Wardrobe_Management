from wardrobe.models import WardrobeItem
from accessories.models import Accessory
from .models import OutfitRecommendation, AccessoryRecommendation


def generate_outfit_recommendations(user, occasion_id=None, season_id=None):
    """
    Final working logic:
    - Case-insensitive category match
    - No empty-string filtering
    - No clean_status blocker
    - No duplicate rows
    """

    # 🔹 Base querysets
    tops = WardrobeItem.objects.filter(
        user=user,
        category__name__iexact='top'
    )

    bottoms = WardrobeItem.objects.filter(
        user=user,
        category__name__iexact='bottom'
    )

    # 🔹 Safe filtering
    if occasion_id:
        tops = tops.filter(occasion_id=occasion_id)
        bottoms = bottoms.filter(occasion_id=occasion_id)

    if season_id:
        tops = tops.filter(season_id=season_id)
        bottoms = bottoms.filter(season_id=season_id)

    # 🔹 Generate combinations
    for top in tops:
        for bottom in bottoms:
            score = calculate_match_score(top, bottom)

            rec, created = OutfitRecommendation.objects.update_or_create(
                user=user,
                top_item=top,
                bottom_item=bottom,
                defaults={'match_score': score}
            )

            # 🔹 Rebuild accessories
            rec.accessory_recommendations.all().delete()
            recommend_accessories(
                outfit=rec,
                top=top,
                bottom=bottom,
                occasion_id=occasion_id,
                season_id=season_id
            )


def calculate_match_score(top, bottom):
    score = 0.0

    # Color match
    if top.color and bottom.color:
        if top.color.lower() == bottom.color.lower():
            score += 0.5

    # Cleanliness (only if field exists and is True)
    if getattr(top, 'clean_status', False) and getattr(bottom, 'clean_status', False):
        score += 0.3

    # Base compatibility
    score += 0.2

    return round(score, 2)


def recommend_accessories(outfit, top, bottom, occasion_id=None, season_id=None):
    accessories = Accessory.objects.filter(
        is_active=True,
        stock__gt=0
    )

    for accessory in accessories:
        score = 0.0

        # Color match (flexible)
        if accessory.color:
            if top.color and accessory.color.lower() in top.color.lower():
                score += 0.4
            if bottom.color and accessory.color.lower() in bottom.color.lower():
                score += 0.4

        # Occasion match (NULL-safe)
        if occasion_id and (accessory.occasion_id == occasion_id or accessory.occasion_id is None):
            score += 0.2

        # Season match (NULL-safe)
        if season_id and (accessory.season_id == season_id or accessory.season_id is None):
            score += 0.2

        # Practical threshold
        if score >= 0.4:
            AccessoryRecommendation.objects.create(
                outfit=outfit,
                accessory=accessory,
                score=round(score, 2)
            )
