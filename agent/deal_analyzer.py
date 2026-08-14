"""
Core Deal Analyzer Agent using Claude Vision API and Tool Use

This agent:
1. Analyzes item images using Claude's vision capabilities
2. Uses tool_use to search for comparable prices on the web
3. Scores deals based on comparison analysis
4. Categorizes items (art, furniture, collectibles, etc.)
"""

import anthropic
import base64
import json
import re
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ItemCategory(str, Enum):
    """Item categories with specialized analysis logic"""
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
    """Result of analyzing a listing"""
    item_name: str
    category: ItemCategory
    description: str
    listed_price: float
    estimated_value: float
    deal_score: float  # 0-100, higher is better
    reasoning: str
    comparable_items: list[dict]
    recommendation: str


class DealFinderAgent:
    """
    Main agent that uses Claude to analyze deals with vision + tool use.
    
    Works by:
    1. Receiving listing image and price
    2. Claude analyzes the image and decides what tools to use
    3. Tools search for comparable items/prices online
    4. Claude synthesizes findings into a deal analysis
    """

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        
    def _encode_image(self, image_path: str) -> str:
        """Convert image file to base64 for Claude"""
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")

    def _build_tools(self) -> list[dict]:
        """Define tools Claude can use to research prices"""
        return [
            {
                "name": "search_comparable_items",
                "description": "Search for similar items sold online to find comparable prices. Use this to research what similar items have sold for.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Name of the item to search for (e.g., 'Victorian oil painting', 'mid-century modern chair')"
                        },
                        "search_keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional keywords to narrow search (e.g., artist name, brand, era)"
                        },
                        "price_range_min": {
                            "type": "number",
                            "description": "Minimum price to search for"
                        },
                        "price_range_max": {
                            "type": "number",
                            "description": "Maximum price to search for"
                        }
                    },
                    "required": ["item_name"]
                }
            },
            {
                "name": "get_market_value",
                "description": "Get estimated market value for a specific item category based on recent sales data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": [cat.value for cat in ItemCategory],
                            "description": "Item category"
                        },
                        "item_description": {
                            "type": "string",
                            "description": "Detailed description of the item"
                        },
                        "condition": {
                            "type": "string",
                            "enum": ["poor", "fair", "good", "excellent"],
                            "description": "Condition of the item"
                        }
                    },
                    "required": ["category", "condition"]
                }
            },
            {
                "name": "search_artist_prices",
                "description": "For art pieces: search for auction records and gallery prices for a specific artist",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "artist_name": {
                            "type": "string",
                            "description": "Name of the artist"
                        },
                        "art_style": {
                            "type": "string",
                            "description": "Art style or movement (e.g., impressionism, abstract)"
                        },
                        "medium": {
                            "type": "string",
                            "description": "Medium used (oil, watercolor, sculpture, etc.)"
                        }
                    },
                    "required": ["artist_name"]
                }
            }
        ]

    def _process_tool_use(self, tool_name: str, tool_input: dict) -> str:
        """
        Process tool calls. In production, this would make real API calls.
        For now, returns mock data for demo purposes.
        """
        if tool_name == "search_comparable_items":
            return json.dumps({
                "found": True,
                "similar_items": [
                    {
                        "name": tool_input.get("item_name"),
                        "sold_price": tool_input.get("price_range_max", 500) * 0.8,
                        "source": "eBay",
                        "condition": "good",
                        "date": "2024-01-15"
                    },
                    {
                        "name": tool_input.get("item_name"),
                        "sold_price": tool_input.get("price_range_max", 500) * 0.9,
                        "source": "Auction.com",
                        "condition": "excellent",
                        "date": "2024-01-10"
                    }
                ]
            })
        
        elif tool_name == "get_market_value":
            condition_multipliers = {
                "poor": 0.3,
                "fair": 0.6,
                "good": 0.8,
                "excellent": 1.0
            }
            base_value = 300
            multiplier = condition_multipliers.get(tool_input.get("condition", "good"), 0.8)
            return json.dumps({
                "estimated_value": base_value * multiplier,
                "confidence": 0.75,
                "market_trend": "stable"
            })
        
        elif tool_name == "search_artist_prices":
            return json.dumps({
                "artist": tool_input.get("artist_name"),
                "average_price": 2500,
                "price_range": [1000, 15000],
                "recent_sales": 5,
                "market_trend": "increasing"
            })
        
        return json.dumps({"error": "Unknown tool"})

    def analyze_listing(
        self,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        listing_title: str = "",
        listing_price: float = 0.0,
        listing_description: str = ""
    ) -> DealAnalysis:
        """
        Main method: Analyze a garage sale/estate sale listing.
        
        This is where agentic loop happens:
        1. Claude looks at image + description
        2. Claude decides which tools to use
        3. Tools run (or we provide mock data)
        4. Claude synthesizes analysis + scoring
        """
        
        # Build the initial message for Claude
        content = []
        
        # Add image if provided
        if image_path:
            image_data = self._encode_image(image_path)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data
                }
            })
        elif image_url:
            content.append({
                "type": "image",
                "source": {
                    "type": "url",
                    "url": image_url
                }
            })
        
        # Add text analysis request
        analysis_prompt = f"""
        Analyze this item from a garage/estate sale listing for deal potential.
        
        Listing Information:
        - Title: {listing_title}
        - Listed Price: ${listing_price}
        - Description: {listing_description}
        
        Please:
        1. Identify what the item is
        2. Categorize it (art, furniture, collectibles, jewelry, vintage, books, electronics, home decor)
        3. Assess its condition from the image
        4. Use the search tools to find comparable market prices
        5. Provide an estimated fair market value
        6. Score this as a deal (0-100, where 100 is an exceptional deal)
        7. Explain your reasoning
        
        Return your analysis in JSON format with these fields:
        - item_name
        - category
        - description
        - condition
        - estimated_value
        - deal_score
        - reasoning
        - recommendation
        """
        
        content.append({
            "type": "text",
            "text": analysis_prompt
        })
        
        # Start agentic loop
        messages = [{"role": "user", "content": content}]
        
        while True:
            # Call Claude with tools available
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                tools=self._build_tools(),
                messages=messages
            )
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Process each tool use in the response
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_result = self._process_tool_use(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result
                        })
                
                # Add Claude's response and tool results to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
                
            else:
                # Claude finished - extract the analysis
                break
        
        # Parse Claude's final response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text = block.text
                break
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
        if json_match:
            analysis_data = json.loads(json_match.group())
        else:
            analysis_data = {}
        
        # Create DealAnalysis object
        category_str = analysis_data.get("category", "unknown").lower()
        try:
            category = ItemCategory(category_str)
        except ValueError:
            category = ItemCategory.UNKNOWN
        
        return DealAnalysis(
            item_name=analysis_data.get("item_name", listing_title),
            category=category,
            description=analysis_data.get("description", listing_description),
            listed_price=listing_price,
            estimated_value=analysis_data.get("estimated_value", listing_price),
            deal_score=analysis_data.get("deal_score", 50),
            reasoning=analysis_data.get("reasoning", "Analysis pending"),
            comparable_items=analysis_data.get("comparable_items", []),
            recommendation=analysis_data.get("recommendation", "Investigate further")
        )


if __name__ == "__main__":
    # Example usage
    import os
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    agent = DealFinderAgent(api_key)
    
    # Example without image
    result = agent.analyze_listing(
        listing_title="Vintage Oil Painting - Landscape",
        listing_price=150.0,
        listing_description="Beautiful 19th century oil painting in ornate wooden frame. Minor wear on edges."
    )
    
    print(f"\n{'='*60}")
    print(f"Item: {result.item_name}")
    print(f"Category: {result.category.value}")
    print(f"Listed Price: ${result.listed_price}")
    print(f"Estimated Value: ${result.estimated_value}")
    print(f"Deal Score: {result.deal_score}/100")
    print(f"Recommendation: {result.recommendation}")
    print(f"{'='*60}")
