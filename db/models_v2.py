"""
ENHANCED DATABASE MODELS FOR DEALFINDER V2

This file shows what data we store and why.

KEY CONCEPTS:
1. Listings = Raw data from websites (what we scraped)
2. DealAnalyses = Claude's analysis of each listing
3. Locations = Geocoding (lat/lon) so we can filter by distance
4. PhoneAlerts = Users who want SMS notifications
5. RiskScores = Why a deal might not be good (education/condition/trust)

EXPLANATION OF EACH TABLE:
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    Boolean, Enum, ForeignKey, Table, Index, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ItemCategory(str, enum.Enum):
    """What TYPE of item is this?
    
    Examples:
    - ART: paintings, sculptures
    - FURNITURE: tables, chairs, couches
    - VINTAGE: retro items, antiques
    - JEWELRY: rings, necklaces, watches
    - BOOKS: books, rare editions
    - ELECTRONICS: phones, computers, TVs
    - COLLECTIBLES: action figures, sports cards
    - HOME_DECOR: vases, mirrors, rugs
    """
    ART = "art"
    FURNITURE = "furniture"
    VINTAGE = "vintage"
    JEWELRY = "jewelry"
    BOOKS = "books"
    ELECTRONICS = "electronics"
    COLLECTIBLES = "collectibles"
    HOME_DECOR = "home_decor"
    UNKNOWN = "unknown"


class ItemSize(str, enum.Enum):
    """How big is this item?
    
    SMALL: Can carry by hand (< 5 lbs)
      Example: book, vase, jewelry
    
    MEDIUM: Needs 2 people or small vehicle (5-50 lbs)
      Example: chair, lamp, box of items
    
    LARGE: Needs car/truck (50-500 lbs)
      Example: couch, dresser, dining table
    
    XLARGE: Needs truck + help (> 500 lbs)
      Example: grand piano, wall unit, antique desk
    """
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"
    UNKNOWN = "unknown"


class PickupMethod(str, enum.Enum):
    """How can someone pick this up?
    
    ON_FOOT: Can carry it, no vehicle needed
      Use case: Items < 10 lbs, easy to transport
    
    CAR: Fits in a regular car trunk or back seat
      Use case: Furniture that fits in sedan, boxes of items
    
    TRUCK: Needs a truck bed or cargo van
      Use case: Large furniture, multiple boxes
    
    TRAILER: Needs a trailer or large truck
      Use case: Very large items, multiple furniture pieces
    
    DELIVERY: They deliver it to you!
      Use case: Heavy items, person wants to avoid pickup
    """
    ON_FOOT = "on_foot"
    CAR = "car"
    TRUCK = "truck"
    TRAILER = "trailer"
    DELIVERY = "delivery"


class ConditionRating(str, enum.Enum):
    """What condition is the item in?
    
    POOR: Damaged, broken, significant wear
      Risk: May not work or look bad
    
    FAIR: Works but shows wear, some minor damage
      Risk: Might need cleaning/restoration
    
    GOOD: Works well, cosmetic wear, minor issues
      Risk: Acceptable for daily use or restoration
    
    EXCELLENT: Like new, minimal wear, perfect
      Risk: Lowest risk, highest confidence
    """
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class Listing(Base):
    """
    RAW DATA FROM WEBSITES
    
    What it stores: Exactly what we scraped from estate sales websites
    Why: Source of truth for what exists, before Claude analyzes it
    
    Example:
    {
        "title": "Victorian Oil Painting in Frame",
        "price": 150.00,
        "source": "estate_sales_us",
        "location": "Dallas, TX 75201",
        "latitude": 32.7765,
        "longitude": -96.7969
    }
    """
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True)
    
    # ===== BASIC INFO =====
    title = Column(String(255), nullable=False)
    description = Column(Text)
    listed_price = Column(Float, nullable=False)
    
    # ===== SOURCE INFO =====
    source = Column(String(50), nullable=False)  # "estate_sales_us", "craigslist", etc
    source_url = Column(String(500), unique=True, nullable=False)
    image_urls = Column(JSON)  # List of photo URLs
    
    # ===== LOCATION INFO (IMPORTANT FOR FILTERING!) =====
    # Why we store this: So users can filter "deals near me"
    location_name = Column(String(255))  # "Dallas, TX 75201"
    latitude = Column(Float)  # 32.7765 (north/south position)
    longitude = Column(Float)  # -96.7969 (east/west position)
    zip_code = Column(String(10))  # "75201" (for quick filtering)
    city = Column(String(100))  # "Dallas"
    state = Column(String(2))  # "TX"
    
    # ===== SIZE & PICKUP INFO =====
    # Why: Users filter by "things I can carry" vs "need a truck"
    estimated_size = Column(Enum(ItemSize), default=ItemSize.UNKNOWN)
    suggested_pickup_methods = Column(JSON)  # List of PickupMethod values
    
    # ===== TIMESTAMPS =====
    listed_date = Column(DateTime)  # When it was posted (estate sale date)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Still available?
    
    # ===== RELATIONSHIPS =====
    analysis = relationship("DealAnalysis", back_populates="listing", uselist=False)
    
    __table_args__ = (
        Index("idx_location", "latitude", "longitude"),  # Fast geo searches
        Index("idx_zip_code", "zip_code"),  # Fast zip code searches
        Index("idx_city", "city"),  # Find deals in one city
        Index("idx_is_active", "is_active"),  # Only show active deals
    )


class DealAnalysis(Base):
    """
    CLAUDE'S ANALYSIS OF EACH LISTING
    
    What it stores: What Claude thinks about the item
    Why: Answers "Is this a good deal?" and "Should I get it?"
    
    This is where Claude's intelligence is captured!
    
    Example:
    {
        "item_name": "Victorian Oil Painting",
        "category": "art",
        "estimated_value": 500.0,
        "deal_score": 85,
        "risk_score": 15,  # NEW: How risky is this deal?
        "confidence": 0.82
    }
    """
    __tablename__ = "deal_analyses"
    
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False, unique=True)
    
    # ===== ITEM IDENTIFICATION =====
    # What is this thing?
    item_name = Column(String(255), nullable=False)
    category = Column(Enum(ItemCategory), default=ItemCategory.UNKNOWN)
    condition = Column(Enum(ConditionRating), default=ConditionRating.GOOD)
    
    # ===== VALUE ANALYSIS =====
    # Claude researched comparable prices
    estimated_value = Column(Float)  # What Claude thinks it's worth
    comparable_items = Column(JSON)  # List of similar items + prices Claude found
    confidence = Column(Float)  # 0-1, how confident in the estimate
    
    # ===== DEAL SCORING (THE MAGIC!) =====
    # Why: Users want to know "Is this good?"
    deal_score = Column(Float, default=50)  # 0-100, higher = better deal
    
    # ===== RISK ANALYSIS (NEW!) =====
    # Why: Just because it's cheap doesn't mean it's good
    # Risk score = 100 - deal_score (roughly)
    # But broken down by category:
    risk_score = Column(Float, default=50)  # 0-100, higher = more risky
    
    # Risk breakdown (for explaining to user):
    authenticity_risk = Column(Float)  # Is it real? (for art)
    condition_risk = Column(Float)  # Will it work/last?
    hidden_cost_risk = Column(Float)  # Shipping? Restoration? Delivery?
    market_risk = Column(Float)  # Might not sell if reselling
    
    # ===== EXPLANATIONS FOR USER =====
    # Why we give them this: Users want to UNDERSTAND the score
    # NOT just "85/100 - buy it!"
    # But "85/100 because it's 70% below market value, condition is excellent"
    
    score_explanation = Column(Text)  # "Why is this an 85?"
    # Example: "Victorian oil painting valued at $500+ in auctions.
    #          Listed at $150 = 70% discount.
    #          Condition is excellent with no visible damage.
    #          Only risk: Artist unknown (common for 19th century works)."
    
    risk_explanation = Column(Text)  # "Why is there risk?"
    # Example: "Risk: Artist is unknown, makes authentication difficult.
    #          Cost to restore frame: ~$50.
    #          Could be harder to resell than famous artists.
    #          Recommendation: Research artist if planning to resell."
    
    # ===== SPECIAL CATEGORIES (EXPANDABLE) =====
    # For art specifically:
    artist_name = Column(String(255))
    art_style = Column(String(100))
    period = Column(String(100))  # "19th century"
    provenance = Column(Text)  # History/proof of authenticity
    
    # For furniture:
    designer = Column(String(255))  # "Mid-century modern"
    era = Column(String(100))  # "1950s"
    
    # ===== TIMESTAMPS =====
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))  # Which Claude model analyzed this
    
    # ===== RELATIONSHIPS =====
    listing = relationship("Listing", back_populates="analysis")
    
    __table_args__ = (
        Index("idx_deal_score", "deal_score"),  # Sort by best deals
        Index("idx_risk_score", "risk_score"),  # Sort by safest deals
        Index("idx_category", "category"),  # Filter by type
    )


class PhoneAlert(Base):
    """
    USER PREFERENCES FOR SMS ALERTS
    
    What it stores: "I want texts when you find deals matching these criteria"
    Why: Users don't check website, we push notifications to them
    
    Example:
    {
        "phone": "+1-512-123-4567",
        "interested_categories": ["art", "vintage"],
        "max_distance_miles": 10,
        "pickup_methods": ["on_foot", "car"],
        "min_deal_score": 75,
        "max_price": 500
    }
    """
    __tablename__ = "phone_alerts"
    
    id = Column(Integer, primary_key=True)
    
    # ===== USER CONTACT =====
    phone_number = Column(String(20), nullable=False, unique=True)
    
    # ===== PREFERENCES =====
    # What deals do they care about?
    interested_categories = Column(JSON)  # ["art", "vintage", "furniture"]
    
    # ===== LOCATION FILTER =====
    # Only show deals nearby
    user_latitude = Column(Float)  # Their location
    user_longitude = Column(Float)
    user_zip_code = Column(String(10))  # Or by zip
    user_city = Column(String(100))
    max_distance_miles = Column(Float, default=10)  # "Show me deals within 10 miles"
    
    # ===== SIZE & PICKUP FILTER =====
    # Can they actually pick it up?
    acceptable_sizes = Column(JSON)  # ["small", "medium"]
    acceptable_pickup_methods = Column(JSON)  # ["on_foot", "car"]
    
    # ===== DEAL FILTER =====
    min_deal_score = Column(Integer, default=70)  # Only "good deals"
    max_price = Column(Float)  # Budget limit
    
    # ===== ALERT FREQUENCY =====
    alerts_per_day = Column(Integer, default=5)  # Don't spam them
    last_alert_sent = Column(DateTime)
    
    # ===== STATUS =====
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_phone", "phone_number"),
        Index("idx_zip_code", "user_zip_code"),
    )


class AlertHistory(Base):
    """
    LOG OF ALERTS SENT
    
    What it stores: "We sent phone +1-512-123-4567 about deal #42 on Jan 15"
    Why: 
    1. Track what we told them (avoid duplicate alerts)
    2. Analytics (which deals get shared most?)
    3. User can see "deals you've been alerted about"
    """
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    analysis_id = Column(Integer, ForeignKey("deal_analyses.id"))
    
    deal_score_at_send = Column(Float)  # What was score when we alerted?
    price_at_send = Column(Float)  # What was price when we alerted?
    
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_phone_sent", "phone_number", "sent_at"),
        Index("idx_deal_sent", "analysis_id", "sent_at"),
    )


class ScraperMetrics(Base):
    """
    MONITORING THE SCRAPERS
    
    What it stores: "Scraper ran at 10 AM, found 50 new deals, 2 errors"
    Why: Know if scrapers are working or broken
    """
    __tablename__ = "scraper_metrics"
    
    id = Column(Integer, primary_key=True)
    
    scraper_name = Column(String(100))  # "estate_sales_us"
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    
    items_found = Column(Integer, default=0)
    items_analyzed = Column(Integer, default=0)
    alerts_sent = Column(Integer, default=0)
    
    errors = Column(Integer, default=0)
    runtime_seconds = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    __table_args__ = (
        Index("idx_scraper_time", "scraper_name", "run_timestamp"),
    )


"""
=====================================================
SUMMARY: How the tables work together
=====================================================

USER JOURNEY:
1. User enters phone + interests
2. System saves in PhoneAlert table

SCRAPING PROCESS:
1. Scraper finds listing on estatesales.us
2. Save to Listings table
3. Claude analyzes it
4. Save to DealAnalyses table
5. Calculate risk scores
6. Write explanations

ALERT PROCESS:
1. Check PhoneAlert table: Who wants Art deals?
2. Get deal from DealAnalyses
3. Calculate: Is this deal close enough? (distance)
4. Is this deal pickupable? (size + methods)
5. Is deal score >= their minimum?
6. If YES: Send SMS via Twilio
7. Log in AlertHistory table

WEBSITE SHOWS:
1. Get deals from DealAnalyses
2. Calculate distance from user's location
3. Show with deal_score + risk_score
4. Show explanations so user understands

=====================================================
"""
