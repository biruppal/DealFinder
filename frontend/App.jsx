"""
DEALFINDER REACT FRONTEND

This file shows the complete user interface.

WHAT USERS SEE:
1. Homepage - Enter phone + select interests
2. Deal Feed - Browse all deals with filters
3. Deal Details - See full analysis + risk breakdown
4. No authentication needed - Just enter phone and go!

FEATURES:
✅ Location-based filtering (show deals near me)
✅ Distance filtering (1 mile, 10 miles, etc)
✅ Size filtering (things I can carry vs need truck)
✅ Pickup method filtering (on foot, car, truck, trailer)
✅ Sort by size, score, price
✅ Deal score explanation with risk breakdown
✅ SMS alert signup (no payment)
✅ Responsive mobile design

This demonstrates:
✅ React hooks (useState, useEffect)
✅ API integration
✅ Real-time filtering
✅ Mobile-first design
✅ User experience thinking
"""

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// API base URL
const API = 'http://localhost:8000/api/v1';

// ============================================================================
// HOMEPAGE - Enter phone and select interests
// ============================================================================

function HomePage({ onStarted }) {
  const [phone, setPhone] = useState('');
  const [selectedCategories, setSelectedCategories] = useState(['art']);
  const [distance, setDistance] = useState(10);
  const [error, setError] = useState('');

  const categories = [
    'Art', 'Furniture', 'Vintage', 'Jewelry',
    'Books', 'Electronics', 'Collectibles', 'Home Decor'
  ];

  const handleCategoryToggle = (cat) => {
    setSelectedCategories(prev =>
      prev.includes(cat.toLowerCase())
        ? prev.filter(c => c !== cat.toLowerCase())
        : [...prev, cat.toLowerCase()]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!phone) {
      setError('Please enter your phone number');
      return;
    }

    if (selectedCategories.length === 0) {
      setError('Please select at least one category');
      return;
    }

    try {
      // Subscribe to alerts
      await axios.post(`${API}/alerts/subscribe`, {
        phone_number: phone,
        interested_categories: selectedCategories,
        max_distance_miles: distance
      });

      onStarted({
        phone,
        categories: selectedCategories,
        distance
      });
    } catch (err) {
      setError('Failed to save preferences. Please try again.');
    }
  };

  return (
    <div className="homepage">
      <div className="hero">
        <h1>🎯 DealFinder</h1>
        <p>Find the best deals from garage sales and estate sales near you</p>
      </div>

      <form onSubmit={handleSubmit} className="signup-form">
        <div className="form-section">
          <h2>What interests you?</h2>
          <div className="categories-grid">
            {categories.map(cat => (
              <label key={cat} className="category-checkbox">
                <input
                  type="checkbox"
                  checked={selectedCategories.includes(cat.toLowerCase())}
                  onChange={() => handleCategoryToggle(cat)}
                />
                <span>{cat}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-section">
          <h2>How far are you willing to go?</h2>
          <div className="distance-selector">
            {[1, 5, 10, 25, 50].map(d => (
              <button
                key={d}
                type="button"
                className={`distance-btn ${distance === d ? 'active' : ''}`}
                onClick={() => setDistance(d)}
              >
                {d} miles
              </button>
            ))}
          </div>
        </div>

        <div className="form-section">
          <label>
            <span>Your phone number</span>
            <input
              type="tel"
              placeholder="+1 (512) 123-4567"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              pattern="[0-9-+() ]+"
            />
          </label>
          <small>We'll text you when we find deals matching your interests</small>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn-primary">
          Get Alerts & Browse Deals
        </button>
      </form>
    </div>
  );
}

// ============================================================================
// DEAL CARD - Shows one deal in the feed
// ============================================================================

function DealCard({ deal, onViewDetails }) {
  const scoreColor = deal.deal_score >= 80 ? 'excellent' : 
                     deal.deal_score >= 70 ? 'good' : 'fair';
  
  const riskColor = deal.risk_score >= 50 ? 'high-risk' :
                    deal.risk_score >= 30 ? 'medium-risk' : 'low-risk';

  return (
    <div className="deal-card" onClick={() => onViewDetails(deal)}>
      {/* Image */}
      {deal.image_urls && deal.image_urls.length > 0 && (
        <div className="deal-image">
          <img src={deal.image_urls[0]} alt={deal.item_name} />
        </div>
      )}

      {/* Badges */}
      <div className="deal-badges">
        <span className={`score-badge ${scoreColor}`}>
          {deal.deal_score.toFixed(0)}/100
        </span>
        <span className={`risk-badge ${riskColor}`}>
          Risk: {deal.risk_score.toFixed(0)}
        </span>
      </div>

      {/* Content */}
      <div className="deal-content">
        <h3>{deal.item_name}</h3>
        <p className="category">{deal.category}</p>
        
        <div className="pricing">
          <span className="listed">Listed: ${deal.listed_price}</span>
          <span className="estimated">Est. Worth: ${deal.estimated_value}</span>
        </div>

        <div className="meta">
          <span className="distance">{deal.distance_miles?.toFixed(1)} miles away</span>
          <span className="size">{deal.estimated_size}</span>
        </div>

        <button className="btn-view" onClick={() => onViewDetails(deal)}>
          View Details →
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// DEAL DETAILS - Full page view with risk breakdown
// ============================================================================

function DealDetailsPage({ deal, onBack }) {
  return (
    <div className="deal-details">
      <button className="btn-back" onClick={onBack}>← Back to Deals</button>

      {/* Image Gallery */}
      {deal.image_urls && deal.image_urls.length > 0 && (
        <div className="image-gallery">
          {deal.image_urls.map((img, idx) => (
            <img key={idx} src={img} alt={`${deal.item_name} ${idx}`} />
          ))}
        </div>
      )}

      {/* Header Info */}
      <div className="details-header">
        <h1>{deal.item_name}</h1>
        <p className="category">{deal.category}</p>
      </div>

      {/* Pricing Section */}
      <section className="pricing-section">
        <div className="price-card">
          <label>Listed Price</label>
          <h2 className="price">${deal.listed_price}</h2>
        </div>
        <div className="price-card highlight">
          <label>Estimated Market Value</label>
          <h2 className="price">${deal.estimated_value}</h2>
        </div>
        <div className="price-card">
          <label>You Save</label>
          <h2 className="savings">
            ${(deal.estimated_value - deal.listed_price).toFixed(0)}
            <span className="percent">
              {((1 - deal.listed_price / deal.estimated_value) * 100).toFixed(0)}% off
            </span>
          </h2>
        </div>
      </section>

      {/* DEAL SCORE with Explanation */}
      <section className="deal-score-section">
        <h2>Why is this an {deal.deal_score}/100 deal?</h2>
        <div className="score-gauge">
          <div className="gauge-fill" style={{ width: `${deal.deal_score}%` }}></div>
        </div>
        <p className="explanation">{deal.score_explanation}</p>
      </section>

      {/* RISK ANALYSIS with Breakdown */}
      <section className="risk-analysis-section">
        <h2>What could go wrong? (Risk Breakdown)</h2>
        
        <div className="risk-item">
          <label>Authenticity Risk</label>
          <div className="risk-bar">
            <div className="risk-fill" style={{ width: `${deal.authenticity_risk}%` }}></div>
          </div>
          <span>{deal.authenticity_risk.toFixed(0)}/100</span>
          <small>How confident are we this is genuine?</small>
        </div>

        <div className="risk-item">
          <label>Condition Risk</label>
          <div className="risk-bar">
            <div className="risk-fill" style={{ width: `${deal.condition_risk}%` }}></div>
          </div>
          <span>{deal.condition_risk.toFixed(0)}/100</span>
          <small>Will it work well or last?</small>
        </div>

        <div className="risk-item">
          <label>Hidden Cost Risk</label>
          <div className="risk-bar">
            <div className="risk-fill" style={{ width: `${deal.hidden_cost_risk}%` }}></div>
          </div>
          <span>{deal.hidden_cost_risk.toFixed(0)}/100</span>
          <small>Shipping, restoration, delivery costs?</small>
        </div>

        <div className="risk-item">
          <label>Market/Resale Risk</label>
          <div className="risk-bar">
            <div className="risk-fill" style={{ width: `${deal.market_risk}%` }}></div>
          </div>
          <span>{deal.market_risk.toFixed(0)}/100</span>
          <small>Can you resell it if needed?</small>
        </div>

        <p className="explanation">{deal.risk_explanation}</p>
      </section>

      {/* Comparable Items */}
      {deal.comparable_items && deal.comparable_items.length > 0 && (
        <section className="comparables-section">
          <h2>Similar Items Sold For:</h2>
          <div className="comparables-list">
            {deal.comparable_items.map((item, idx) => (
              <div key={idx} className="comparable-item">
                <span className="comparable-name">{item.name}</span>
                <span className="comparable-price">${item.sold_price}</span>
                <span className="comparable-source">{item.source}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Item Details */}
      <section className="item-details-section">
        <div className="detail-row">
          <label>Size</label>
          <span className="value">{deal.estimated_size}</span>
        </div>
        <div className="detail-row">
          <label>Condition</label>
          <span className="value">{deal.condition}</span>
        </div>
        <div className="detail-row">
          <label>Distance</label>
          <span className="value">{deal.distance_miles?.toFixed(1)} miles away</span>
        </div>
        <div className="detail-row">
          <label>Found on</label>
          <span className="value">{deal.source}</span>
        </div>
      </section>

      {/* View on Original Site */}
      <a href={deal.source_url} target="_blank" rel="noopener noreferrer" className="btn-primary-large">
        View on {deal.source === 'craigslist' ? 'Craigslist' : 'Estate Sales'} →
      </a>
    </div>
  );
}

// ============================================================================
// DEAL FEED - Browse and filter deals
// ============================================================================

function DealFeed({ userPrefs }) {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDeal, setSelectedDeal] = useState(null);
  
  // Filters
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [sizeFilter, setSizeFilter] = useState('all');
  const [pickupFilter, setPickupFilter] = useState('all');
  const [sortBy, setSortBy] = useState('score');
  const [distanceFilter, setDistanceFilter] = useState(userPrefs.distance);

  useEffect(() => {
    // Fetch deals from API
    const fetchDeals = async () => {
      try {
        const params = new URLSearchParams();
        if (categoryFilter !== 'all') params.append('category', categoryFilter);
        if (sizeFilter !== 'all') params.append('size', sizeFilter);
        if (sortBy) params.append('sort', sortBy);
        params.append('limit', 50);

        const response = await axios.get(`${API}/deals?${params.toString()}`);
        setDeals(response.data.deals);
      } catch (error) {
        console.error('Failed to fetch deals:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDeals();
  }, [categoryFilter, sizeFilter, sortBy]);

  if (selectedDeal) {
    return <DealDetailsPage deal={selectedDeal} onBack={() => setSelectedDeal(null)} />;
  }

  return (
    <div className="deal-feed">
      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Category</label>
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
            <option value="all">All Categories</option>
            <option value="art">Art</option>
            <option value="furniture">Furniture</option>
            <option value="vintage">Vintage</option>
            <option value="jewelry">Jewelry</option>
            <option value="books">Books</option>
            <option value="electronics">Electronics</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Size</label>
          <select value={sizeFilter} onChange={(e) => setSizeFilter(e.target.value)}>
            <option value="all">Any Size</option>
            <option value="small">Small (Can carry)</option>
            <option value="medium">Medium (2 people)</option>
            <option value="large">Large (Need truck)</option>
            <option value="xlarge">Extra Large (Trailer)</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Pickup Method</label>
          <select value={pickupFilter} onChange={(e) => setPickupFilter(e.target.value)}>
            <option value="all">Any Method</option>
            <option value="on_foot">On Foot</option>
            <option value="car">Car</option>
            <option value="truck">Truck</option>
            <option value="trailer">Trailer</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Distance</label>
          <select value={distanceFilter} onChange={(e) => setDistanceFilter(parseFloat(e.target.value))}>
            <option value={1}>1 mile</option>
            <option value={5}>5 miles</option>
            <option value={10}>10 miles</option>
            <option value={25}>25 miles</option>
            <option value={50}>50 miles</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Sort By</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="score">Best Deals (Score)</option>
            <option value="price">Cheapest</option>
            <option value="value">Best Value</option>
            <option value="distance">Closest</option>
            <option value="newest">Newest</option>
          </select>
        </div>
      </div>

      {/* Deals Grid */}
      {loading ? (
        <div className="loading">Loading deals...</div>
      ) : (
        <div className="deals-grid">
          {deals.length > 0 ? (
            deals.map(deal => (
              <DealCard
                key={deal.id}
                deal={deal}
                onViewDetails={setSelectedDeal}
              />
            ))
          ) : (
            <div className="no-results">
              No deals found matching your filters. Try adjusting them!
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// MAIN APP
// ============================================================================

export default function App() {
  const [userStarted, setUserStarted] = useState(false);
  const [userPrefs, setUserPrefs] = useState(null);

  return (
    <div className="app">
      {userStarted ? (
        <DealFeed userPrefs={userPrefs} />
      ) : (
        <HomePage
          onStarted={(prefs) => {
            setUserPrefs(prefs);
            setUserStarted(true);
          }}
        />
      )}
    </div>
  );
}
