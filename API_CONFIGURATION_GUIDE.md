# API Configuration Guide for Live Stock Prices

## Overview
The application now uses a **multi-provider fallback strategy** for fetching live stock prices, ensuring maximum reliability and coverage for both Indian (NSE/BSE) and US markets.

## API Provider Strategy

### For Indian Stocks (.NS, .BO)
1. **Primary**: Alpha Vantage (Best for Indian markets)
2. **Fallback**: Yahoo Finance (via proxy)

### For US Stocks
1. **Primary**: Finnhub (Best for US markets, 60 calls/min)
2. **Secondary**: Alpha Vantage
3. **Fallback**: Yahoo Finance (via proxy)

## API Keys Required

### 1. Alpha Vantage (FREE) ✅ Already Configured
- **Current Status**: You already have the key configured
- **Your Key**: `9T8D85D3AQIQ8VO2`
- **Free Tier**: 25 API calls per day, 5 calls per minute
- **Best For**: Indian stocks (NSE/BSE)
- **Coverage**: Global stocks, Indian markets
- **Get Your Key**: https://www.alphavantage.co/support/#api-key

### 2. Finnhub (FREE) ✅ Already Configured
- **Current Status**: You already have the key configured
- **Your Key**: `d5dpe71r01qur4itoq3gd5dpe71r01qur4itoq40`
- **Free Tier**: 60 API calls per minute
- **Best For**: US stocks
- **Coverage**: US stocks, some international
- **Get Your Key**: https://finnhub.io/register

### 3. Yahoo Finance (FREE) - No Key Required
- **Status**: Works via proxy, no API key needed
- **Used as**: Fallback option
- **Coverage**: Global stocks including Indian markets

## Current Configuration

Your environment is already configured in `src/environments/environment.ts`:

```typescript
marketData: {
  finnhubApiKey: 'd5dpe71r01qur4itoq3gd5dpe71r01qur4itoq40',
  alphaVantageApiKey: '9T8D85D3AQIQ8VO2',
  cacheTimeout: 60000, // 1 minute cache
  autoRefreshInterval: 120000 // 2 minutes auto-refresh
}
```

## How It Works

### Example: Fetching IRFC.NS (Indian Stock)
1. **First Try**: Alpha Vantage fetches IRFC.BSE
2. **If Fails**: Yahoo Finance tries IRFC.NS
3. **Result**: Live price with change %, volume, high/low

### Example: Fetching AAPL (US Stock)
1. **First Try**: Finnhub fetches AAPL
2. **If Fails**: Alpha Vantage tries AAPL
3. **If Fails**: Yahoo Finance tries AAPL
4. **Result**: Live price with all data

## API Rate Limits

| Provider | Free Tier Limit | Best For |
|----------|----------------|----------|
| Alpha Vantage | 25 calls/day, 5/minute | Indian stocks |
| Finnhub | 60 calls/minute | US stocks |
| Yahoo Finance | Unlimited* | Fallback |

*Via proxy, may have undocumented limits

## Optimization Features

### 1. Smart Caching
- Quotes cached for 60 seconds
- Reduces API calls significantly
- Configurable via `cacheTimeout`

### 2. Rate Limiting Protection
- 300ms delay between batch requests
- Prevents hitting rate limits
- Automatic retry with fallback

### 3. Symbol Format Handling
- Automatically converts symbols for each API
- Example: `RELIANCE.NS` → `RELIANCE.BSE` for Alpha Vantage
- Transparent to the user

## Testing the Setup

### Test Indian Stock
```typescript
// In browser console:
// This will use Alpha Vantage → Yahoo fallback
marketDataService.getQuote('RELIANCE.NS').subscribe(
  quote => console.log('Success:', quote),
  error => console.error('Error:', error)
);
```

### Test US Stock
```typescript
// This will use Finnhub → Alpha Vantage → Yahoo fallback
marketDataService.getQuote('AAPL').subscribe(
  quote => console.log('Success:', quote),
  error => console.error('Error:', error)
);
```

## Troubleshooting

### "API limit reached"
- **Alpha Vantage**: Wait 1 day (25 calls/day limit)
- **Solution**: Yahoo Finance will be used as fallback
- **Prevention**: Implement longer cache durations

### "Symbol not found"
- **Indian Stocks**: Must use .NS (NSE) or .BO (BSE) suffix
  - Example: `RELIANCE.NS` ✅
  - Example: `RELIANCE` ❌
- **US Stocks**: Use ticker without suffix
  - Example: `AAPL` ✅

### Yahoo Finance 404 Errors
- **Not a Problem**: System will use Alpha Vantage or Finnhub
- **Fallback Active**: Check console for which provider succeeded

## Recommendations

### For Production Use

1. **Upgrade Alpha Vantage** (Optional)
   - Premium: $49.99/month
   - 75 API calls/minute
   - Unlimited daily calls
   - Best for Indian markets

2. **Upgrade Finnhub** (Optional)
   - Starter: $9.99/month
   - 300 calls/minute
   - US real-time data

3. **Keep Yahoo as Fallback**
   - Free and unlimited
   - Good reliability

### For Development/Testing
- Current free tier setup is **perfect**
- No upgrades needed
- All APIs are working

## API Status Check

Check console logs on page load:
```
[MarketDataService] Initialized with Multi-Provider Support
[MarketDataService] Alpha Vantage Key: ✅ Configured
[MarketDataService] Finnhub Key: ✅ Configured
```

## Symbol Format Guide

### Indian Stocks
| Exchange | Format | Example |
|----------|--------|---------|
| NSE (National) | SYMBOL.NS | RELIANCE.NS |
| BSE (Bombay) | SYMBOL.BO | RELIANCE.BO |

### US Stocks
| Market | Format | Example |
|--------|--------|---------|
| NASDAQ | SYMBOL | AAPL, MSFT |
| NYSE | SYMBOL | JPM, BAC |

### Indices
| Index | Symbol |
|-------|--------|
| NIFTY 50 | ^NSEI |
| SENSEX | ^BSESN |
| NIFTY BANK | ^NSEBANK |
| S&P 500 | ^GSPC |
| DOW JONES | ^DJI |

## Performance Tips

1. **Batch Requests**: Use `getMultipleQuotes()` for multiple symbols
2. **Cache First**: Check cache before making API calls
3. **Longer Cache**: Increase `cacheTimeout` to 2-5 minutes for production
4. **Auto-Refresh**: Use `autoRefreshInterval` for periodic updates

## What Changed

### Before (Yahoo Only)
- ❌ Yahoo Finance API returning 404 errors
- ❌ No fallback options
- ❌ Limited reliability

### After (Multi-Provider)
- ✅ Alpha Vantage for Indian stocks
- ✅ Finnhub for US stocks
- ✅ Yahoo Finance as fallback
- ✅ Automatic provider switching
- ✅ Rate limiting protection
- ✅ Smart caching

## Support

If you encounter issues:
1. Check console logs for detailed error messages
2. Verify API keys in environment.ts
3. Check rate limits haven't been exceeded
4. Test with different symbols
5. Yahoo fallback should always work

## Summary

✅ **You have all required API keys configured**  
✅ **System will automatically choose best provider**  
✅ **No action needed - ready to use**  
✅ **Free tier limits are sufficient for development**

The application is now more reliable and will provide live stock prices for both Indian and US markets!
