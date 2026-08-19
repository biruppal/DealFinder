"""
DEALFINDER API - MOCKED VERSION

Works without real Claude API or database.
Perfect for testing and demos locally!

Just replace the mock functions with real ones for production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="DealFinder API (MOCKED)",
    description="AI-powered deal finder - Mock version for testing",
    version="2.0.0-mock"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class DealAnalysisResponse(BaseModel):
    """One deal with all analysis"""
    id: int
    item_name: str
    category: str
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
    source: str
    source_url: str
    image_urls: List[str]
    location_name: str
    latitude: float
    longitude: float
    distance_miles: Optional[float] = None
    estimated_size: str
    suggested_pickup_methods: List[str]
    comparable_items: List[dict]


class DealListResponse(BaseModel):
    """Paginated list of deals"""
    deals: List[DealAnalysisResponse]
    total: int
    returned: int


class AlertSubscriptionRequest(BaseModel):
    """User subscribes to alerts"""
    phone_number: str
    interested_categories: List[str]
    max_distance_miles: float = 10
    min_deal_score: int = 70
    max_price: Optional[float] = None


class AlertSubscriptionResponse(BaseModel):
    """Confirmation"""
    phone_number: str
    status: str
    message: str


# ============================================================================
# MOCK DATA
# ============================================================================

MOCK_DEALS = [
    {
        "id": 1,
        "item_name": "Victorian Oil Painting",
        "category": "art",
        "listed_price": 150,
        "estimated_value": 500,
        "deal_score": 85,
        "risk_score": 15,
        "authenticity_risk": 10,
        "condition_risk": 5,
        "hidden_cost_risk": 10,
        "market_risk": 20,
        "score_explanation": "Victorian oil painting valued at $500+ in auctions. Listed at $150 = 70% discount. Condition is excellent with no visible damage.",
        "risk_explanation": "Risk: Artist unknown, makes authentication difficult. Could need frame restoration ($50). Harder to resell than famous artists.",
        "source": "estatesales_us",
        "source_url": "https://estatesales.us/sales/1234",
        "image_urls": ["https://via.placeholder.com/300x300?text=Painting"],
        "location_name": "Dallas, TX 75201",
        "latitude": 32.7765,
        "longitude": -96.7969,
        "distance_miles": 2.5,
        "estimated_size": "medium",
        "suggested_pickup_methods": ["car", "truck"],
        "comparable_items": [
            {"name": "Similar oil painting", "sold_price": 450, "source": "eBay"},
            {"name": "Victorian landscape", "sold_price": 520, "source": "Auction"},
        ]
    },
    {
        "id": 2,
        "item_name": "Mid-Century Modern Sofa",
        "category": "furniture",
        "listed_price": 300,
        "estimated_value": 800,
        "deal_score": 78,
        "risk_score": 22,
        "authenticity_risk": 0,
        "condition_risk": 20,
        "hidden_cost_risk": 30,
        "market_risk": 10,
        "score_explanation": "Mid-century sofa typically sells for $800-1000. Listed at $300 = 62% off retail. Good condition with minimal wear.",
        "risk_explanation": "Condition: Check for structural integrity, fabric stains. Delivery will cost $100-200. May need reupholstering ($300-500).",
        "source": "craigslist",
        "source_url": "https://dallas.craigslist.org/",
        "image_urls": ["https://via.placeholder.com/300x300?text=Sofa"],
        "location_name": "Dallas, TX 75204",
        "latitude": 32.8116,
        "longitude": -96.7890,
        "distance_miles": 4.2,
        "estimated_size": "large",
        "suggested_pickup_methods": ["truck", "trailer"],
        "comparable_items": [
            {"name": "Similar mid-century sofa", "sold_price": 750, "source": "Facebook"},
            {"name": "Eames-style sofa", "sold_price": 900, "source": "Craigslist"},
        ]
    },
    {
        "id": 3,
        "item_name": "Vintage Rolex Watch",
        "category": "jewelry",
        "listed_price": 450,
        "estimated_value": 1200,
        "deal_score": 88,
        "risk_score": 12,
        "authenticity_risk": 25,
        "condition_risk": 8,
        "hidden_cost_risk": 5,
        "market_risk": 10,
        "score_explanation": "Vintage Rolex watches sell for $1000-1500. Listed at $450 = 62% below market. Excellent find if authentic.",
        "risk_explanation": "Authenticity: MUST verify with certified watch expert ($50-100). Condition: Working well, normal patina. Gold content makes it always resellable.",
        "source": "estate_sales_us",
        "source_url": "https://estatesales.us/sales/5678",
        "image_urls": ["https://via.placeholder.com/300x300?text=Watch"],
        "location_name": "Austin, TX 78701",
        "latitude": 30.2672,
        "longitude": -97.7431,
        "distance_miles": 195.0,
        "estimated_size": "small",
        "suggested_pickup_methods": ["on_foot", "car"],
        "comparable_items": [
            {"name": "Rolex Submariner, vintage", "sold_price": 1200, "source": "eBay"},
            {"name": "Rolex Datejust, 1970s", "sold_price": 1400, "source": "Auction"},
        ]
    },
    {
        "id": 4,
        "item_name": "Antique Secretary Desk",
        "category": "furniture",
        "listed_price": 200,
        "estimated_value": 600,
        "deal_score": 82,
        "risk_score": 18,
        "authenticity_risk": 15,
        "condition_risk": 18,
        "hidden_cost_risk": 20,
        "market_risk": 12,
        "score_explanation": "Antique secretary desks sell for $500-700. Listed at $200 = 66% discount. Beautiful woodwork, authentic period piece.",
        "risk_explanation": "Authenticity: Verify age and maker with antique expert. Condition: Check for loose joints, drawer function. Restoration could cost $200+.",
        "source": "garage_sale_finder",
        "source_url": "https://garagesalefinder.com/sales/austin",
        "image_urls": ["https://via.placeholder.com/300x300?text=Desk"],
        "location_name": "Austin, TX 78704",
        "latitude": 30.2500,
        "longitude": -97.7500,
        "distance_miles": 190.0,
        "estimated_size": "large",
        "suggested_pickup_methods": ["truck", "trailer"],
        "comparable_items": [
            {"name": "Mahogany secretary desk", "sold_price": 650, "source": "Antique dealer"},
            {"name": "Victorian secretary", "sold_price": 700, "source": "Auction"),
        ]
    },
    {
        "id": 5,
        "item_name": "Rare First Edition Book",
        "category": "books",
        "listed_price": 75,
        "estimated_value": 350,
        "deal_score": 79,
        "risk_score": 21,
        "authenticity_risk": 20,
        "condition_risk": 15,
        "hidden_cost_risk": 5,
        "market_risk": 25,
        "score_explanation": "First edition books of this title sell for $300-400. Listed at $75 = 78% discount! Exceptional value if authentic.",
        "risk_explanation": "Authenticity: Verify edition and printing details. Condition: Check binding, page quality. Market: Niche collector market.",
        "source": "craigslist",
        "source_url": "https://dallas.craigslist.org/",
        "image_urls": ["https://via.placeholder.com/300x300?text=Book"],
        "location_name": "Dallas, TX 75202",
        "latitude": 32.7880,
        "longitude": -96.8080,
        "distance_miles": 1.2,
        "estimated_size": "small",
        "suggested_pickup_methods": ["on_foot", "car"],
        "comparable_items": [
            {"name": "Same first edition", "sold_price": 380, "source": "AbeBooks"},
            {"name": "First printing copy", "sold_price": 350, "source": "eBay"},
        ]
    }
]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "name": "DealFinder API (MOCKED)",
        "version": "2.0.0-mock",
        "message": "This is a mocked version - no real Claude API calls",
        "docs": "/docs"
    }


@app.get("/api/v1/deals", response_model=DealListResponse)
async def get_deals(
    category: Optional[str] = None,
    size: Optional[str] = None,
    min_score: int = 0,
    max_price: Optional[float] = None,
    sort: str = "score",
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    max_distance: float = 50,
    limit: int = 50,
    offset: int = 0,
):
    """Get all deals with filtering (MOCKED DATA)"""
    
    deals = MOCK_DEALS.copy()
    
    # Filter by score
    deals = [d for d in deals if d["deal_score"] >= min_score]
    
    # Filter by price
    if max_price:
        deals = [d for d in deals if d["listed_price"] <= max_price]
    
    # Filter by category
    if category:
        deals = [d for d in deals if d["category"].lower() == category.lower()]
    
    # Sort
    if sort == "score":
        deals.sort(key=lambda x: x["deal_score"], reverse=True)
    elif sort == "price":
        deals.sort(key=lambda x: x["listed_price"])
    elif sort == "distance":
        deals.sort(key=lambda x: x["distance_miles"] or float('inf'))
    
    # Pagination
    total = len(deals)
    deals = deals[offset:offset + limit]
    
    return DealListResponse(
        deals=deals,
        total=total,
        returned=len(deals)
    )


@app.get("/api/v1/deals/{deal_id}")
async def get_deal_detail(deal_id: int):
    """Get one deal with full analysis"""
    deal = next((d for d in MOCK_DEALS if d["id"] == deal_id), None)
    if not deal:
        return {"error": "Deal not found"}
    return deal


@app.post("/api/v1/alerts/subscribe", response_model=AlertSubscriptionResponse)
async def subscribe_to_alerts(request: AlertSubscriptionRequest):
    """User subscribes to SMS alerts (MOCKED)"""
    
    return AlertSubscriptionResponse(
        phone_number=request.phone_number,
        status="success",
        message=f"✅ Alerts enabled for {', '.join(request.interested_categories)}! We'll text you when we find deals matching your interests."
    )


@app.get("/api/v1/stats")
async def get_stats():
    """Overall statistics"""
    return {
        "total_deals": len(MOCK_DEALS),
        "total_alerts_sent": 1250,
        "avg_deal_score": 82.4,
        "categories": {
            "art": 245,
            "furniture": 380,
            "jewelry": 80,
            "vintage": 195,
            "books": 90,
            "electronics": 120,
            "collectibles": 70,
            "home_decor": 20
        },
        "last_scrape": datetime.now().isoformat(),
        "mode": "MOCKED - No real API calls"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "mode": "mocked"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_mocked:app", host="0.0.0.0", port=8000, reload=True)
