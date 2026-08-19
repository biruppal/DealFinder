"""
DEALFINDER SCORING ENGINE - MOCKED VERSION

This version uses mock data instead of real Claude API calls.
Perfect for testing locally without needing API credits.

In production, replace the mock_analyze() calls with real Claude API.
"""

import json
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ItemCategory(str, Enum):
    """Item types"""
    ART = "art"
    FURNITURE = "furniture"
    COLLECTIBLES = "collectibles"
    JEWELRY = "jewelry"
    VINTAGE = "vintage"
    BOOKS = "books"
    ELECTRONICS = "electronics"
    HOME_DECOR = "home_decor"
    UNKNOWN = "unknown"


@dataclass
class DealAnalysis:
    """Complete analysis of a listing"""
    item_name: str
    category: ItemCategory
    listed_price: float
    estimated_value: float
    deal_score: float
    risk_score: float
    authenticity_risk: float
    condition_risk: float
    hidden_cost_risk: float
    market_risk: float
    score_explanation: str
    risk_explanation: str
    confidence: float
    comparable_items: list


class DealScoringEngine:
    """
    Deal Scoring Engine with MOCKED Claude API
    
    This works without real API keys - perfect for testing!
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize engine.
        
        api_key: Not needed for mocked version, but kept for compatibility
        """
        self.mock_mode = True  # Always use mock data
        logger.info("DealScoringEngine initialized in MOCK MODE")
    
    def score_deal(
        self,
        listing_title: str,
        listed_price: float,
        listing_description: str,
        image_path: Optional[str] = None,
        location: str = "Unknown"
    ) -> DealAnalysis:
        """
        Analyze and score a deal using MOCK data.
        
        Returns realistic mock data for testing without API calls.
        """
        
        logger.info(f"Scoring deal (MOCK): {listing_title} at ${listed_price}")
        
        # Generate realistic mock analysis based on item type
        return self._mock_analyze(
            listing_title,
            listed_price,
            listing_description,
            location
        )
    
    def _mock_analyze(
        self,
        title: str,
        price: float,
        description: str,
        location: str
    ) -> DealAnalysis:
        """
        Generate realistic mock analysis data.
        
        This mimics what Claude would return for different item types.
        """
        
        title_lower = title.lower()
        desc_lower = description.lower()
        combined = f"{title_lower} {desc_lower}".lower()
        
        # Determine category
        category = self._mock_categorize(combined)
        
        # Generate mock scores based on category
        if category == ItemCategory.ART:
            return self._mock_art_deal(title, price, location)
        elif category == ItemCategory.FURNITURE:
            return self._mock_furniture_deal(title, price, location)
        elif category == ItemCategory.JEWELRY:
            return self._mock_jewelry_deal(title, price, location)
        elif category == ItemCategory.ELECTRONICS:
            return self._mock_electronics_deal(title, price, location)
        elif category == ItemCategory.VINTAGE:
            return self._mock_vintage_deal(title, price, location)
        else:
            return self._mock_generic_deal(title, price, category, location)
    
    def _mock_categorize(self, text: str) -> ItemCategory:
        """Determine category from text"""
        if any(word in text for word in ['painting', 'art', 'artist', 'canvas', 'sculpture']):
            return ItemCategory.ART
        elif any(word in text for word in ['chair', 'table', 'sofa', 'desk', 'furniture', 'couch']):
            return ItemCategory.FURNITURE
        elif any(word in text for word in ['ring', 'necklace', 'bracelet', 'watch', 'jewelry']):
            return ItemCategory.JEWELRY
        elif any(word in text for word in ['phone', 'computer', 'tv', 'electronics', 'laptop']):
            return ItemCategory.ELECTRONICS
        elif any(word in text for word in ['vintage', 'antique', 'retro', 'old', '1950s', '1960s']):
            return ItemCategory.VINTAGE
        else:
            return ItemCategory.UNKNOWN
    
    def _mock_art_deal(self, title: str, price: float, location: str) -> DealAnalysis:
        """Mock analysis for art pieces"""
        
        # Art pieces typically sell for $400-600
        estimated_value = 500.0
        discount_pct = (1 - price / estimated_value) * 100
        deal_score = min(95, 50 + (discount_pct * 0.5))  # Better score for bigger discount
        
        return DealAnalysis(
            item_name=title,
            category=ItemCategory.ART,
            listed_price=price,
            estimated_value=estimated_value,
            deal_score=deal_score,
            risk_score=100 - deal_score,
            authenticity_risk=15,  # Art authenticity is always a concern
            condition_risk=5,
            hidden_cost_risk=10,  # Frame restoration costs
            market_risk=20,  # Harder to resell
            score_explanation=f"Comparable art pieces sell for ~${estimated_value}. Listed at ${price} = {discount_pct:.0f}% discount. Condition appears excellent with no visible damage. Excellent value for collectors.",
            risk_explanation="Authenticity: Artist unknown, makes verification difficult. Cost: Frame restoration may cost $50-100. Market: Niche market, slower to sell than famous artists.",
            confidence=0.82,
            comparable_items=[
                {"name": "Similar oil painting", "sold_price": 450, "source": "eBay"},
                {"name": "Landscape painting, similar period", "sold_price": 520, "source": "Auction.com"},
                {"name": "Oil on canvas, 20x24", "sold_price": 480, "source": "Facebook Marketplace"}
            ]
        )
    
    def _mock_furniture_deal(self, title: str, price: float, location: str) -> DealAnalysis:
        """Mock analysis for furniture"""
        
        # Furniture typically 30-50% of retail
        estimated_value = price * 2.5  # Estimate based on listed price
        discount_pct = (1 - price / estimated_value) * 100
        deal_score = min(90, 40 + (discount_pct * 0.4))
        
        return DealAnalysis(
            item_name=title,
            category=ItemCategory.FURNITURE,
            listed_price=price,
            estimated_value=estimated_value,
            deal_score=deal_score,
            risk_score=100 - deal_score,
            authenticity_risk=0,
            condition_risk=15,  # Furniture condition matters
            hidden_cost_risk=20,  # Delivery/repair costs
            market_risk=10,
            score_explanation=f"Similar furniture pieces retail for ${estimated_value:.0f}. Listed at ${price} = {discount_pct:.0f}% below retail. Good condition reported.",
            risk_explanation="Condition: Check for structural issues, fabric wear. Cost: Delivery may be $50-150. Repairs: Reupholstering could cost $200+.",
            confidence=0.78,
            comparable_items=[
                {"name": "Same furniture type, retail", "sold_price": int(estimated_value), "source": "West Elm"},
                {"name": "Used version, good condition", "sold_price": int(estimated_value * 0.6), "source": "Facebook"},
            ]
        )
    
    def _mock_jewelry_deal(self, title: str, price: float, location: str) -> DealAnalysis:
        """Mock analysis for jewelry"""
        
        # Jewelry resale is typically 40-60% of retail
        estimated_value = price / 0.45  # Assume this is 45% of value
        discount_pct = (1 - price / estimated_value) * 100
        deal_score = min(95, 45 + (discount_pct * 0.45))
        
        return DealAnalysis(
            item_name=title,
            category=ItemCategory.JEWELRY,
            listed_price=price,
            estimated_value=estimated_value,
            deal_score=deal_score,
            risk_score=100 - deal_score,
            authenticity_risk=25,  # Jewelry authenticity concerns
            condition_risk=10,
            hidden_cost_risk=5,
            market_risk=15,
            score_explanation=f"Similar jewelry pieces valued at ${estimated_value:.0f}. Listed at ${price} = {discount_pct:.0f}% below market. Excellent value if authentic.",
            risk_explanation="Authenticity: Verify with jeweler, test metals/stones. Certification may cost $50-100. Resale: Gold/silver always resellable.",
            confidence=0.75,
            comparable_items=[
                {"name": "Similar jewelry piece", "sold_price": int(estimated_value * 0.8), "source": "eBay"},
                {"name": "Gold jewelry, similar weight", "sold_price": int(estimated_value * 0.75), "source": "Pawn shop"},
            ]
        )
    
    def _mock_electronics_deal(self, title: str, price: float, location: str) -> DealAnalysis:
        """Mock analysis for electronics"""
        
        # Electronics depreciate quickly
        estimated_value = price * 1.8
        discount_pct = (1 - price / estimated_value) * 100
        deal_score = min(85, 40 + (discount_pct * 0.35))
        
        return DealAnalysis(
            item_name=title,
            category=ItemCategory.ELECTRONICS,
            listed_price=price,
            estimated_value=estimated_value,
            deal_score=deal_score,
            risk_score=100 - deal_score,
            authenticity_risk=5,
            condition_risk=20,  # Electronics can fail
            hidden_cost_risk=15,  # Repairs expensive
            market_risk=25,  # Tech depreciates fast
            score_explanation=f"Similar electronics sell for ${estimated_value:.0f}. Listed at ${price} = {discount_pct:.0f}% off. Good deal if working properly.",
            risk_explanation="Condition: Test thoroughly before purchase. Warranty: Likely expired. Repairs: Can be expensive, $100+.",
            confidence=0.70,
            comparable_items=[
                {"name": "Same model, new", "sold_price": int(estimated_value * 1.2), "source": "Best Buy"},
                {"name": "Used version", "sold_price": int(estimated_value * 0.7), "source": "eBay"},
            ]
        )
    
    def _mock_vintage_deal(self, title: str, price: float, location: str) -> DealAnalysis:
        """Mock analysis for vintage items"""
        
        estimated_value = price * 2.0  # Vintage often underpriced
        discount_pct = (1 - price / estimated_value) * 100
        deal_score = min(92, 50 + (discount_pct * 0.42))
        
        return DealAnalysis(
            item_name=title,
            category=ItemCategory.VINTAGE,
            listed_price=price,
            estimated_value=estimated_value,
            deal_score=deal_score,
            risk_score=100 - deal_score,
            authenticity_risk=20,
            condition_risk=12,
            hidden_cost_risk=8,
            market_risk=15,
            score_explanation=f"Vintage pieces of this type typically fetch ${estimated_value:.0f}. Listed at ${price} = {discount_pct:.0f}% below market. Collector's item.",
            risk_explanation="Authenticity: Verify age and maker. Condition: Normal wear expected for vintage. Market: Strong interest in vintage items currently.",
            confidence=0.80,
            comparable_items=[
                {"name": "Same vintage item, good condition", "sold_price": int(estimated_value * 0.9), "source": "Etsy"},
                {"name": "Similar era piece", "sold_price": int(estimated_value * 0.85), "source": "Auction"},
            ]
        )
    
    def _mock_generic_deal(
        self,
        title: str,
        price: float,
        category: ItemCategory,
        location: str
    ) -> DealAnalysis:
        """Mock analysis for unknown item types"""
        
        # Generic analysis
        estimated_value = price * 1.5
        discount_pct = (1 - price / estimated_value) * 100
        deal_score = 50 + (discount_pct * 0.3)
        
        return DealAnalysis(
            item_name=title,
            category=category,
            listed_price=price,
            estimated_value=estimated_value,
            deal_score=min(80, deal_score),
            risk_score=100 - deal_score,
            authenticity_risk=10,
            condition_risk=15,
            hidden_cost_risk=10,
            market_risk=20,
            score_explanation=f"Item listed at ${price}. Estimated market value ${estimated_value:.0f}. {discount_pct:.0f}% below estimate. Appears to be fairly priced.",
            risk_explanation="Condition and authenticity should be verified before purchase. Research comparable sales online.",
            confidence=0.65,
            comparable_items=[
                {"name": "Similar item", "sold_price": int(estimated_value * 0.8), "source": "Online"},
            ]
        )


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    engine = DealScoringEngine()
    
    # Test with mock Victorian painting
    analysis = engine.score_deal(
        listing_title="Victorian Oil Painting - Landscape",
        listed_price=150.0,
        listing_description="Beautiful 19th century oil painting in ornate wooden frame. Minor wear on edges. Approximately 24x30 inches.",
        location="Dallas, TX"
    )
    
    print(f"\n{'='*70}")
    print(f"DEAL ANALYSIS: {analysis.item_name}")
    print(f"{'='*70}")
    print(f"Listed Price: ${analysis.listed_price}")
    print(f"Estimated Value: ${analysis.estimated_value}")
    print(f"Value-to-Price Ratio: {(analysis.estimated_value/analysis.listed_price):.1f}x")
    print(f"\nDeal Score: {analysis.deal_score:.0f}/100")
    print(f"Risk Score: {analysis.risk_score:.0f}/100")
    print(f"\nWhy this score:")
    print(f"{analysis.score_explanation}")
    print(f"\nRisks to consider:")
    print(f"{analysis.risk_explanation}")
    print(f"\nComparable items found:")
    for item in analysis.comparable_items:
        print(f"  - {item['name']}: ${item['sold_price']} ({item['source']})")
    print(f"{'='*70}")
