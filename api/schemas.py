"""
Pydantic schemas for API request/response validation.

These ensure type safety, generate OpenAPI documentation,
and validate incoming data.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DealAnalysisResponse(BaseModel):
    """Single deal analysis result"""
    id: int
    item_name: str = Field(..., description="Identified item name")
    category: str = Field(..., description="Item category (art, furniture, etc.)")
    condition: str = Field(default="good", description="Item condition rating")
    detailed_description: Optional[str] = None
    
    # Pricing
    listed_price: float = Field(..., description="Price at the sale")
    estimated_value: float = Field(..., description="Estimated fair market value")
    value_to_price_ratio: float = Field(..., description="How much below market")
    
    # Scoring
    deal_score: float = Field(..., ge=0, le=100, description="Deal quality 0-100")
    recommendation: str = Field(..., description="excellent_deal, good_deal, fair, overpriced")
    reasoning: str = Field(..., description="Why this is/isn't a good deal")
    
    # Market data
    comparable_items: List[Dict[str, Any]] = Field(default=[], description="Similar items and prices")
    
    # Category-specific
    artist_name: Optional[str] = None
    art_style: Optional[str] = None
    provenance: Optional[str] = None
    
    # Listing details
    source: str = Field(..., description="Where the listing was found")
    source_url: str = Field(..., description="Link to original listing")
    listed_date: datetime = Field(..., description="When it was listed")
    image_urls: List[str] = Field(default=[], description="Photos of the item")
    
    # Metadata
    analyzed_at: datetime = Field(..., description="When Claude analyzed it")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "item_name": "Victorian Oil Painting",
                "category": "art",
                "condition": "good",
                "listed_price": 150.0,
                "estimated_value": 500.0,
                "value_to_price_ratio": 3.33,
                "deal_score": 85,
                "recommendation": "excellent_deal",
                "reasoning": "19th century oil painting, well below auction estimates",
                "artist_name": "Unknown European",
                "source": "estate_sales_us",
                "source_url": "https://...",
            }
        }


class DealListResponse(BaseModel):
    """Paginated list of deals"""
    deals: List[DealAnalysisResponse]
    total: int = Field(..., description="Total matching deals")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Pagination offset")
    returned: int = Field(..., description="Items returned in this response")


class ListingResponse(BaseModel):
    """Raw listing from a sale website"""
    id: int
    source: str
    source_url: str
    title: str
    listed_price: float
    image_urls: List[str]
    location: Optional[str] = None
    listed_date: datetime


class UserSubscriptionRequest(BaseModel):
    """Request to subscribe to alerts"""
    email: EmailStr = Field(..., description="Email for alerts")
    categories: List[str] = Field(default=["art"], description="Interested categories")
    min_deal_score: int = Field(default=70, ge=0, le=100, description="Minimum deal score")
    max_price: Optional[float] = Field(default=None, description="Maximum price filter")
    telegram_user_id: Optional[str] = None
    discord_user_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "collector@example.com",
                "categories": ["art", "vintage"],
                "min_deal_score": 75,
                "max_price": 1000.0,
                "telegram_user_id": "123456789"
            }
        }


class UserSubscriptionResponse(BaseModel):
    """Confirmation of subscription"""
    user_id: str
    email: str
    categories: List[str]
    min_deal_score: int
    subscription_active: bool
    created_at: Optional[datetime] = None


class ArtistAnalysisResponse(BaseModel):
    """Artist-specific analysis for art deals"""
    artist_name: str
    average_market_price: float
    price_range: tuple[float, float] = Field(..., description="Min and max prices")
    recent_sales: int = Field(..., description="Number of recent sales")
    market_trend: str = Field(..., description="increasing, stable, or decreasing")
    deals_found: int = Field(default=0, description="How many deals found for this artist")
    best_deal_id: Optional[int] = None


class CategoryStatsResponse(BaseModel):
    """Statistics for a category"""
    category: str
    total_deals: int
    avg_deal_score: float
    avg_discount_percentage: float = Field(..., description="Average % below market")
    recent_listings: int = Field(..., description="Listings in past 7 days")


class AlertNotification(BaseModel):
    """Notification sent to user about a new deal"""
    user_id: str
    deal_id: int
    item_name: str
    category: str
    deal_score: float
    listed_price: float
    estimated_value: float
    why_relevant: str = Field(..., description="Why we're notifying about this deal")
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: str
    timestamp: datetime


# ============================================================================
# Internal request/response models (not exposed in API)
# ============================================================================

class ImageAnalysisRequest(BaseModel):
    """Internal request for image analysis"""
    listing_id: int
    image_url: str
    image_data: Optional[str] = None  # base64


class AnalysisResult(BaseModel):
    """Internal result from Claude analysis"""
    item_name: str
    category: str
    condition: str
    estimated_value: float
    deal_score: float
    comparable_items: List[Dict[str, Any]]
    recommendation: str
    reasoning: str
