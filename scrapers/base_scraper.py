"""
Base scraper class using inheritance and abstract methods.

This demonstrates:
- Clean architecture pattern
- DRY principle (Don't Repeat Yourself)
- Easy to add new sources
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScrapedListing:
    """Standardized format for listings from any source"""
    source: str
    source_url: str
    title: str
    price: float
    description: Optional[str]
    image_urls: List[str]
    location: Optional[str] = None
    zip_code: Optional[str] = None
    sale_date: Optional[datetime] = None
    listed_date: Optional[datetime] = None


class BaseScraper(ABC):
    """
    Abstract base scraper that all sources inherit from.
    
    Usage:
    ```python
    scraper = EstateSalesUSScraper()
    listings = scraper.scrape()
    for listing in listings:
        print(listing.title, listing.price)
    ```
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the source (e.g., 'estate_sales_us')"""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL for the website"""
        pass
    
    @abstractmethod
    def scrape(self) -> List[ScrapedListing]:
        """Main scraping method - must be implemented by subclasses"""
        pass
    
    def _fetch(self, url: str) -> Optional[str]:
        """
        Safely fetch a URL with retries and error handling.
        
        Returns HTML content or None if failed.
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Fetch attempt {attempt+1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
        return None
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """
        Convert price strings like "$150.00", "150", "150-200" to float.
        
        Returns first price in range, or None if can't parse.
        """
        try:
            # Remove common price prefixes
            cleaned = price_str.replace("$", "").replace(",", "").split("-")[0].strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse price: {price_str}")
            return None
    
    def _normalize_listing(self, listing: ScrapedListing) -> ScrapedListing:
        """
        Validate and normalize a listing.
        
        Returns listing if valid, or None if should be skipped.
        """
        if not listing.title or listing.price is None:
            return None
        
        if listing.price <= 0:
            logger.warning(f"Invalid price for {listing.title}: {listing.price}")
            return None
        
        # Ensure source is set
        listing.source = self.source_name
        
        return listing
    
    def close(self):
        """Clean up resources"""
        self.session.close()


class EstateSalesUSScraper(BaseScraper):
    """
    Scraper for Estate Sales USA (estatesales.us)
    
    Demonstrates:
    - Parsing real website structure
    - Handling pagination
    - Image extraction
    """
    
    @property
    def source_name(self) -> str:
        return "estate_sales_us"
    
    @property
    def base_url(self) -> str:
        return "https://www.estatesales.us"
    
    def scrape(self) -> List[ScrapedListing]:
        """
        Scrape estate sales listings.
        
        In real implementation, would:
        1. Visit estatesales.us
        2. Parse listing cards
        3. Extract price, title, images, location
        4. Handle pagination
        """
        listings = []
        
        logger.info(f"Starting scrape of {self.source_name}")
        
        try:
            # Example: scrape first page
            url = f"{self.base_url}/search/?s=&c=&state=%20"
            html = self._fetch(url)
            
            if not html:
                return []
            
            # In real implementation:
            # from bs4 import BeautifulSoup
            # soup = BeautifulSoup(html, 'html.parser')
            # listing_cards = soup.find_all('div', class_='sale-card')
            # for card in listing_cards:
            #     listing = self._parse_listing_card(card)
            #     if self._normalize_listing(listing):
            #         listings.append(listing)
            
            logger.info(f"Scraped {len(listings)} listings from {self.source_name}")
            return listings
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
            return []
    
    def _parse_listing_card(self, card) -> Optional[ScrapedListing]:
        """Parse a single listing card from HTML"""
        # In real implementation, would extract:
        # - title from card.find('h3')
        # - price from card.find('span', class_='price')
        # - images from card.find_all('img')
        # - location from card.find('span', class_='location')
        pass


class CraigslistGarageSaleScraper(BaseScraper):
    """
    Scraper for Craigslist garage sales
    
    Demonstrates:
    - Working with different website structure
    - Handling listings without consistent format
    """
    
    @property
    def source_name(self) -> str:
        return "craigslist"
    
    @property
    def base_url(self) -> str:
        return "https://www.craigslist.org"
    
    def scrape(self) -> List[ScrapedListing]:
        """Scrape Craigslist garage sale listings"""
        listings = []
        
        logger.info(f"Starting scrape of {self.source_name}")
        
        try:
            # In real implementation:
            # 1. Visit craigslist.org/search/gra (garage sales)
            # 2. Parse listing items
            # 3. Extract all relevant fields
            # 4. Handle pagination
            
            logger.info(f"Scraped {len(listings)} listings from {self.source_name}")
            return listings
        
        except Exception as e:
            logger.error(f"Error scraping {self.source_name}: {e}")
            return []


class GarageSaleFinderScraper(BaseScraper):
    """
    Scraper for GarageSaleFinder.com
    
    Demonstrates:
    - Specialized garage sale aggregator
    """
    
    @property
    def source_name(self) -> str:
        return "garage_sale_finder"
    
    @property
    def base_url(self) -> str:
        return "https://www.garagesalefinder.com"
    
    def scrape(self) -> List[ScrapedListing]:
        """Scrape garage sale finder listings"""
        listings = []
        
        logger.info(f"Starting scrape of {self.source_name}")
        
        # Implementation here
        
        return listings


def get_all_scrapers() -> List[BaseScraper]:
    """Factory function to get all available scrapers"""
    return [
        EstateSalesUSScraper(),
        CraigslistGarageSaleScraper(),
        GarageSaleFinderScraper(),
    ]


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    scraper = EstateSalesUSScraper()
    listings = scraper.scrape()
    
    for listing in listings[:5]:  # Show first 5
        print(f"\n{listing.title}")
        print(f"  Price: ${listing.price}")
        print(f"  Location: {listing.location}")
    
    scraper.close()
