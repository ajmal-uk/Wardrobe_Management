from wardrobe.models import WardrobeItem
from accessories.models import Accessory
from .models import OutfitRecommendation, AccessoryRecommendation


# ==========================================================
# 🎨 COLOR GROUPS (GENERIC)
# ==========================================================

NEUTRALS = {'black', 'white', 'gray', 'beige', 'cream'}
STRONG_COLORS = {'red', 'green', 'yellow'}

# Treat ALL blues as one family
BLUE_FAMILY = {'blue', 'light blue', 'dark blue', 'navy'}
DENIM = {'blue', 'light blue', 'dark blue', 'navy', 'black'}

# ❌ UNIVERSAL CLASHES
BAD_COMBOS = {
    ('red', 'green'),
    ('green', 'red'),
    ('blue', 'green'),
    ('green', 'blue'),
    ('black', 'green'),
    ('green', 'black'),
    ('white', 'green'),
    ('green', 'white'),
}


# ==========================================================
# 👕 OUTFIT GENERATION
# ==========================================================

def generate_outfit_recommendations(user, occasion_id=None, season_id=None):
    tops = WardrobeItem.objects.filter(
        user=user,
        category__name__iexact='top'
    )

    bottoms = WardrobeItem.objects.filter(
        user=user,
        category__name__iexact='bottom'
    )

    if occasion_id:
        tops = tops.filter(occasion_id=occasion_id)
        bottoms = bottoms.filter(occasion_id=occasion_id)

    if season_id:
        tops = tops.filter(season_id=season_id)
        bottoms = bottoms.filter(season_id=season_id)

    for top in tops:
        for bottom in bottoms:
            score = calculate_match_score(top, bottom)

            OutfitRecommendation.objects.update_or_create(
                user=user,
                top_item=top,
                bottom_item=bottom,
                defaults={'match_score': score}
            )


# ==========================================================
# 🧠 MATCH SCORE LOGIC (GENERIC & SCALABLE)
# ==========================================================

def normalize_color(color):
    if not color:
        return ''
    c = color.lower()
    if 'blue' in c:
        return 'blue'
    if 'black' in c:
        return 'black'
    if 'white' in c:
        return 'white'
    if 'green' in c:
        return 'green'
    if 'red' in c:
        return 'red'
    return c


def calculate_match_score(top, bottom):
    top_color = normalize_color(top.color)
    bottom_color = normalize_color(bottom.color)

    # 🚫 HARD BLOCK — NEVER RECOVER
    if (top_color, bottom_color) in BAD_COMBOS:
        return 0.25  # BAD

    score = 0.0

    # ⭐ EXCELLENT: TONAL BLUE / DENIM (YOUR CASE)
    if top_color == 'blue' and bottom_color == 'blue':
        score = 0.85

    # ⭐ EXCELLENT: NEUTRAL HIGH CONTRAST
    elif top_color in NEUTRALS and bottom_color in NEUTRALS:
        score = 0.80

    # ⭐ EXCELLENT: MONOCHROME NEUTRAL
    elif top_color == bottom_color and top_color in NEUTRALS:
        score = 0.85

    # ✅ GOOD: Neutral + Denim
    elif top_color in NEUTRALS and bottom_color in DENIM:
        score = 0.65

    # ⚠️ AVERAGE: One neutral
    elif top_color in NEUTRALS or bottom_color in NEUTRALS:
        score = 0.50

    # ❌ Weak strong-on-strong
    elif top_color in STRONG_COLORS and bottom_color in STRONG_COLORS:
        score = 0.30

    else:
        score = 0.40

    # 🧼 Cleanliness (minor influence)
    if top.clean_status and bottom.clean_status:
        score += 0.10
    else:
        score -= 0.10

    return round(max(0.0, min(score, 1.0)), 2)


# ==========================================================
# 🏷️ SCORE → LABEL (UI)
# ==========================================================

def score_to_label(score):
    if score >= 0.75:
        return "Excellent"
    elif score >= 0.60:
        return "Good"
    elif score >= 0.40:
        return "Average"
    else:
        return "Bad"


# ==========================================================
# 🎒 ACCESSORIES
# ==========================================================

def recommend_accessories(outfit, top, bottom, occasion_id=None, season_id=None):
    accessories = Accessory.objects.filter(is_active=True, stock__gt=0)

    for accessory in accessories:
        score = 0.0

        if accessory.color:
            acc_color = accessory.color.lower()
            if top.color and acc_color in top.color.lower():
                score += 0.4
            if bottom.color and acc_color in bottom.color.lower():
                score += 0.4

        if occasion_id and (accessory.occasion_id == occasion_id or accessory.occasion_id is None):
            score += 0.2

        if season_id and (accessory.season_id == season_id or accessory.season_id is None):
            score += 0.2

        if score >= 0.4:
            AccessoryRecommendation.objects.create(
                outfit=outfit,
                accessory=accessory,
                score=round(score, 2)
            )
