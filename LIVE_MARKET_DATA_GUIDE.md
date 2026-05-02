# Live Market Data Integration Guide

## Overview
Your portfolio now integrates with live market data APIs to provide real-time stock prices, automatic portfolio value updates, and a comprehensive market watchlist feature.

## Features Implemented

### 1. **Live Price Updates for Holdings**
- Add stock symbols (ticker codes) to your investments
- Automatically fetch current prices from market data APIs
- Manual refresh button and auto-refresh every 2 minutes
- Live price indicators with last updated timestamp

### 2. **Smart Symbol Search**
- Search for stocks, ETFs, mutual funds by name or symbol
- Auto-complete with company details
- One-click to auto-fill current price

### 3. **Market Watchlist (Explore Tab)**
- Track favorite stocks without investing
- Real-time price updates with percentage changes
- Detailed quote information (open, high, low, volume, market cap)
- Quick-add popular Indian stocks
- Persistent watchlist saved locally

## Market Data API

### Current Configuration
The app currently uses **Yahoo Finance API** which is:
- ✅ **Free** - No API key required
- ✅ **Real-time data** for global markets
- ✅ **No rate limits** for basic usage
- ✅ **Supports** stocks, ETFs, indices, crypto

### Supported Symbol Formats

#### Indian Stocks (NSE)
Add `.NS` suffix to stock codes:
- `RELIANCE.NS` - Reliance Industries
- `TCS.NS` - Tata Consultancy Services
- `INFY.NS` - Infosys
- `HDFCBANK.NS` - HDFC Bank
- `ICICIBANK.NS` - ICICI Bank

#### Indian Stocks (BSE)
Add `.BO` suffix:
- `RELIANCE.BO`
- `TCS.BO`

#### US Stocks
Use plain ticker symbols:
- `AAPL` - Apple
- `GOOGL` - Google
- `MSFT` - Microsoft
- `TSLA` - Tesla

#### Indian Indices
Use `^` prefix:
- `^NSEI` - Nifty 50
- `^BSESN` - BSE Sensex
- `^NSEBANK` - Bank Nifty

#### Cryptocurrency
Add currency pair suffix:
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum

## How to Use

### Adding Investments with Live Data

1. **Click "Add Investment"** in Holdings tab
2. **Fill investment details** as usual
3. **Enter Stock Symbol** (e.g., `RELIANCE.NS`)
4. **Click refresh button (🔄)** next to symbol field
5. Current price auto-fills from live data
6. Save the investment

### Refreshing Portfolio Prices

**Manual Refresh:**
- Click the **"Refresh"** button in Holdings toolbar
- Updates all investments with stock symbols

**Auto-Refresh:**
- Enabled by default
- Updates every 2 minutes automatically
- Toggle on/off in settings (future enhancement)

### Using the Watchlist (Explore Tab)

1. **Navigate to "Explore"** tab
2. **Search for stocks** using the search bar
3. **Click on search result** to add to watchlist
4. **View live prices** in watchlist cards
5. **Click "Refresh"** to update all watchlist items
6. **Click "✕"** to remove from watchlist

**Quick Add Popular Stocks:**
- Click any chip in "Popular Indian Stocks" section
- Instantly added to watchlist with live data

## Alternative APIs (Optional)

If you need more features or better reliability, consider these alternatives:

### 1. Alpha Vantage (Free Tier)
- **Pros:** Official API, reliable, good documentation
- **Cons:** 25 requests/day limit
- **Setup:**
  1. Get free API key: https://www.alphavantage.co/support/#api-key
  2. Update `environment.ts`:
     ```typescript
     marketDataApi: 'alphavantage',
     alphaVantageKey: 'YOUR_API_KEY'
     ```

### 2. Finnhub (Free Tier)
- **Pros:** 60 requests/minute, excellent for US markets
- **Cons:** Limited Indian stock support
- **Setup:**
  1. Get free API key: https://finnhub.io/register
  2. Update configuration in market-data.service.ts

### 3. IEX Cloud (Free Tier)
- **Pros:** 50,000 messages/month, developer-friendly
- **Cons:** US markets only
- **Setup:**
  1. Get free API key: https://iexcloud.io/
  2. Configure in service

## Configuration

### Environment Variables
File: `src/environments/environment.ts`

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api',
  
  // Market Data Configuration (Optional)
  marketData: {
    provider: 'yahoo', // 'yahoo', 'alphavantage', 'finnhub'
    apiKey: '', // Required for alphavantage, finnhub
    cacheTimeout: 60000, // 1 minute in milliseconds
    autoRefreshInterval: 120000 // 2 minutes
  }
};
```

### Customizing Refresh Intervals

Edit `portfolio-analysis.component.ts`:

```typescript
// Change auto-refresh interval (default: 2 minutes)
this.refreshSubscription = interval(300000) // 5 minutes
  .pipe(switchMap(() => { ... }))
```

## Backend Integration

### Database Schema Update
Add `symbol` field to investment model:

```javascript
// Investment Schema
{
  name: String,
  type: String,
  sector: String,
  symbol: String,  // NEW: Stock ticker symbol
  quantity: Number,
  buyPrice: Number,
  currentPrice: Number,
  date: Date,
  notes: String,
  userId: ObjectId
}
```

### API Endpoints
No changes needed! The existing endpoints automatically handle the new `symbol` field.

## Caching & Performance

### Built-in Caching
- Quotes cached for 1 minute
- Reduces API calls
- Improves performance

### Rate Limiting
- Yahoo Finance: No official limits (use responsibly)
- Alternative APIs: Check their documentation

## Troubleshooting

### Issue: "No data found for symbol"
**Solution:**
- Verify symbol format (e.g., `.NS` for NSE)
- Check if market is open
- Try searching the symbol first

### Issue: CORS errors
**Solution:**
Yahoo Finance API may block browser requests. Consider:
1. Using a CORS proxy in development
2. Implementing backend proxy for production
3. Switching to API with CORS support

### Issue: Prices not updating
**Solution:**
1. Check internet connection
2. Verify symbol is correct
3. Click manual refresh
4. Check browser console for errors

## Privacy & Data

### Local Storage
- Watchlist saved in browser's localStorage
- No personal data sent to external APIs
- Symbol queries are anonymous

### Data Usage
- Only symbol information sent to APIs
- No portfolio values or personal data shared
- Market data APIs track IP addresses (standard practice)

## Future Enhancements

Planned features:
- ✨ Historical price charts in watchlist cards
- ✨ Price alerts and notifications
- ✨ Portfolio performance comparison with indices
- ✨ Sector-wise market sentiment
- ✨ Dividend and earnings data
- ✨ News integration for tracked stocks

## Support

### Popular Resources
- **NSE Symbol Search:** https://www.nseindia.com/
- **BSE Symbol Search:** https://www.bseindia.com/
- **Yahoo Finance:** https://finance.yahoo.com/
- **Investing.com:** https://in.investing.com/

### Tips for Best Results
1. Always use correct symbol format with exchange suffix
2. Refresh during market hours for accurate data
3. Keep watchlist under 50 items for optimal performance
4. Use search feature to find exact symbols

---

**Note:** Market data APIs are provided by third parties. Real-time data accuracy depends on the API provider. This feature is for informational purposes only and should not be considered as financial advice.
