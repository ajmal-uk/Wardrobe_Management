from wardrobe.models import WardrobeItem
from accessories.models import Accessory
from .models import OutfitRecommendation, AccessoryRecommendation


def generate_outfit_recommendations(user, occasion_id=None, season_id=None):
    """
    Logic-only fix:
    - Do NOT create duplicates
    - Update existing rows
    - Keep ONE row per (top, bottom)
    """

    tops = WardrobeItem.objects.filter(
        user=user,
        category__name='Top',
        clean_status=True
    )

    bottoms = WardrobeItem.objects.filter(
        user=user,
        category__name='Bottom',
        clean_status=True
    )

    if occasion_id:
        tops = tops.filter(occasion__id=occasion_id)
        bottoms = bottoms.filter(occasion__id=occasion_id)

    if season_id:
        tops = tops.filter(season__id=season_id)
        bottoms = bottoms.filter(season__id=season_id)

    for top in tops:
        for bottom in bottoms:
            score = calculate_match_score(top, bottom)

            # 🔹 FIND EXISTING RECORD (IF ANY)
            rec = (
                OutfitRecommendation.objects
                .filter(user=user, top_item=top, bottom_item=bottom)
                .order_by('-match_score')
                .first()
            )

            if rec:
                # Update score only if better
                if score > rec.match_score:
                    rec.match_score = score
                    rec.save()
            else:
                rec = OutfitRecommendation.objects.create(
                    user=user,
                    top_item=top,
                    bottom_item=bottom,
                    match_score=score
                )

            # 🔹 Clear old accessories
            rec.accessory_recommendations.all().delete()

            # 🔹 Recompute accessories
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

    # Cleanliness
    if top.clean_status and bottom.clean_status:
        score += 0.3

    # Base compatibility (Top + Bottom)
    score += 0.2

    return round(score, 2)



def recommend_accessories(outfit, top, bottom, occasion_id=None, season_id=None):
    accessories = Accessory.objects.filter(
        is_active=True,
        stock__gt=0
    )

    if occasion_id:
        accessories = accessories.filter(occasion__id=occasion_id)

    if season_id:
        accessories = accessories.filter(season__id=season_id)

    for accessory in accessories:
        score = 0.0

        # Color match
        if accessory.color and top.color and bottom.color:
            if accessory.color.lower() in (
                top.color.lower(),
                bottom.color.lower()
            ):
                score += 0.5

        # Occasion match
        if occasion_id and accessory.occasion_id == occasion_id:
            score += 0.25

        # Season match
        if season_id and accessory.season_id == season_id:
            score += 0.25

        # ✅ ONLY STRONG ACCESSORIES
        if score >= 0.85:
            AccessoryRecommendation.objects.create(
                outfit=outfit,
                accessory=accessory,
                score=round(score, 2)
            )
