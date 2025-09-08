"""
GST Rates as per Indian Government Guidelines
This file contains predefined GST rates for different product categories
"""

# GST Rates for different categories as per Indian Government
GST_RATES = {
    # Essential Items - 0% GST
    'essential_food': 0.00,
    'medicines': 0.00,
    'books': 0.00,
    'newspapers': 0.00,
    
    # Low GST - 5%
    'food_grains': 5.00,
    'milk_products': 5.00,
    'tea_coffee': 5.00,
    'spices': 5.00,
    'sugar': 5.00,
    'edible_oil': 5.00,
    'baby_food': 5.00,
    'footwear_under_1000': 5.00,
    'textiles_under_1000': 5.00,
    
    # Standard GST - 12%
    'mobile_phones': 12.00,
    'computers': 12.00,
    'processed_food': 12.00,
    'ayurvedic_medicines': 12.00,
    'exercise_books': 12.00,
    
    # Higher GST - 18%
    'electronics': 18.00,
    'home_appliances': 18.00,
    'clothing': 18.00,
    'footwear_above_1000': 18.00,
    'cosmetics': 18.00,
    'soaps': 18.00,
    'toothpaste': 18.00,
    'furniture': 18.00,
    'bags': 18.00,
    'watches': 18.00,
    'toys': 18.00,
    'stationery': 18.00,
    'sports_goods': 18.00,
    
    # Luxury Items - 28%
    'automobiles': 28.00,
    'luxury_items': 28.00,
    'air_conditioners': 28.00,
    'refrigerators': 28.00,
    'washing_machines': 28.00,
    'cameras': 28.00,
    'perfumes': 28.00,
    'luxury_watches': 28.00,
    'premium_cars': 28.00,
}

def get_gst_rate(category_name):
    """
    Get GST rate for a category
    Returns 18% as default if category not found
    """
    category_key = category_name.lower().replace(' ', '_')
    return GST_RATES.get(category_key, 18.00)

def get_all_gst_categories():
    """Return all available GST categories"""
    return GST_RATES

# Commission rates for different seller tiers
COMMISSION_RATES = {
    'new_seller': 8.00,      # New sellers pay higher commission
    'regular_seller': 5.00,   # Regular sellers
    'premium_seller': 3.00,   # Premium sellers with high volume
    'enterprise_seller': 2.00 # Enterprise sellers
}

def get_commission_rate(seller_tier='regular_seller'):
    """Get commission rate based on seller tier"""
    return COMMISSION_RATES.get(seller_tier, 5.00)