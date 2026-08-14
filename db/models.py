"""
Database Models for DealFinder

Uses SQLAlchemy for ORM - defines schema for:
- Listings (raw data from scrapers)
- Deal Analyses (Claude's analysis results)
- Users & Alerts (for notifications)
- Tracking (data quality metrics)
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
    """Enum for item categories"""
    ART = "art"
    FURNITURE = "furniture"
    COLLECTIBLES = "collectibles"
    JEWELRY = "jewelry"
    VINTAGE = "vintage"
    BOOKS = "books"
    ELECTRONICS = "electronics"
    HOME_DECOR = "home_decor"
    UNKNOWN = "unknown"


class ConditionRating(str, enum.Enum):
    """Item condition ratings"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class Listing(Base):
    """
    Raw listing from a garage/estate sale website
    
    This is the source data we collect from scrapers.
    Each listing is analyzed once by Claude.
    """
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True)
    
    # Source information
    source = Column(String(50), nullable=False)  # "estate_sales_us", "craigslist", etc.
    source_url = Column(String(500), nullable=False, unique=True)
    
    # Basic listing info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    listed_price = Column(Float, nullable=False)
    
    # Images
    image_urls = Column(JSON)  # List of image URLs
    primary_image_path = Column(String(500))  # Local cached image
    
    # Location
    location = Column(String(255))
    zip_code = Column(String(10))
    
    # Timing
    listed_date = Column(DateTime, default=datetime.utcnow)
    sale_date = Column(DateTime)  # For estate/garage sales
    expiry_date = Column(DateTime)
    
    # Tracking
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    analysis = relationship("DealAnalysis", back_populates="listing", uselist=False)
    price_history = relationship("PriceHistory", back_populates="listing")
    
    __table_args__ = (
        Index("idx_source_url", "source", "source_url"),
        Index("idx_listed_date", "listed_date"),
        Index("idx_is_active", "is_active"),
    )


class DealAnalysis(Base):
    """
    Claude's analysis of a listing - the magic happens here!
    
    Contains:
    - Item identification & categorization
    - Vision-based condition assessment
    - Comparable market prices (from tool use)
    - Deal scoring (0-100)
    - Investment potential
    """
    __tablename__ = "deal_analyses"
    
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False, unique=True)
    
    # Claude's identification
    item_name = Column(String(255), nullable=False)
    category = Column(Enum(ItemCategory), default=ItemCategory.UNKNOWN)
    condition = Column(Enum(ConditionRating), default=ConditionRating.GOOD)
    
    # Vision analysis details
    detailed_description = Column(Text)
    key_features = Column(JSON)  # List of notable features from image
    damage_notes = Column(Text)
    
    # Market analysis
    estimated_market_value = Column(Float)
    price_confidence = Column(Float)  # 0-1, how confident in estimate
    comparable_items = Column(JSON)  # List of dicts with comparable prices
    
    # Scoring
    deal_score = Column(Float, default=50)  # 0-100
    value_to_price_ratio = Column(Float)  # estimated_value / listed_price
    
    # Recommendation
    recommendation = Column(String(50))  # "excellent_deal", "good_deal", "fair", "overpriced"
    reasoning = Column(Text)
    
    # Category-specific
    artist_name = Column(String(255))  # For art
    art_style = Column(String(100))
    provenance = Column(Text)
    
    # Tracking
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))  # Which Claude model
    
    # Relationships
    listing = relationship("Listing", back_populates="analysis")
    alerts = relationship("UserAlert", back_populates="analysis")
    
    __table_args__ = (
        Index("idx_deal_score", "deal_score"),
        Index("idx_category", "category"),
        Index("idx_recommendation", "recommendation"),
    )


class PriceHistory(Base):
    """Track price changes over time for listings"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    
    price = Column(Float, nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow)
    
    listing = relationship("Listing", back_populates="price_history")
    
    __table_args__ = (
        Index("idx_listing_checked", "listing_id", "checked_at"),
    )


class User(Base):
    """Users who want deal notifications"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    
    # Identification
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    
    # Preferences
    preferred_categories = Column(JSON)  # List of ItemCategory values
    min_deal_score = Column(Integer, default=70)  # Only notify on deals >= this score
    max_price = Column(Float)  # Don't show items above this price
    
    # Notification settings
    telegram_user_id = Column(String(100))
    discord_user_id = Column(String(100))
    email_notifications = Column(Boolean, default=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    alerts = relationship("UserAlert", back_populates="user")
    
    __table_args__ = (
        Index("idx_email", "email"),
    )


class UserAlert(Base):
    """Track which deals were notified to which users"""
    __tablename__ = "user_alerts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("deal_analyses.id"), nullable=False)
    
    # Notification status
    sent_at = Column(DateTime)
    channel = Column(String(50))  # "email", "telegram", "discord"
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="alerts")
    analysis = relationship("DealAnalysis", back_populates="alerts")
    
    __table_args__ = (
        Index("idx_user_sent", "user_id", "sent_at"),
        Index("idx_analysis_id", "analysis_id"),
    )


class ScraperMetrics(Base):
    """Track scraper performance and health"""
    __tablename__ = "scraper_metrics"
    
    id = Column(Integer, primary_key=True)
    
    scraper_name = Column(String(100), nullable=False)
    run_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Performance
    items_found = Column(Integer, default=0)
    items_analyzed = Column(Integer, default=0)
    items_with_alerts = Column(Integer, default=0)
    
    # Quality
    errors = Column(Integer, default=0)
    runtime_seconds = Column(Float)
    
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    __table_args__ = (
        Index("idx_scraper_timestamp", "scraper_name", "run_timestamp"),
    )
