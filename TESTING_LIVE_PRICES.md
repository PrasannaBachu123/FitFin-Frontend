# Testing the Live Stock Price Updates

## Quick Test Instructions

### 1. Open your browser's developer console (F12)

### 2. Navigate to Portfolio page
Go to: `http://localhost:4200/dashboard/portfolio`

### 3. Watch the console logs
You should see logs like:
```
[MarketDataService] Initialized with Multi-Provider Support
[MarketDataService] Alpha Vantage Key: ✅ Configured
[MarketDataService] Finnhub Key: ✅ Configured
[Portfolio] Fetching live quotes: ["IRFC.NS", ...]
[MarketData] 🔍 Fetching IRFC.NS...
[AlphaVantage] 🔍 Fetching IRFC.BSE...
[AlphaVantage] ✅ Success for IRFC.NS: {price: 170.50, change: 5.30, ...}
```

### 4. Test in Browser Console

#### Test Indian Stock (IRFC.NS):
```javascript
// Open Console (F12) and run:
const service = document.querySelector('app-portfolio-analysis-component')?.__ngContext__?.[8]?.marketDataService;

if (service) {
  service.getQuote('IRFC.NS').subscribe(
    quote => console.log('✅ Success:', quote),
    error => console.error('❌ Error:', error.message)
  );
}
```

#### Test US Stock (AAPL):
```javascript
service.getQuote('AAPL').subscribe(
  quote => console.log('✅ Success:', quote),
  error => console.error('❌ Error:', error.message)
);
```

## What to Expect

### For Indian Stocks (e.g., IRFC.NS, RELIANCE.NS)
1. **First Try**: Alpha Vantage (Best for Indian markets)
   - Converts IRFC.NS → IRFC.BSE internally
   - Returns live price, change %, volume, etc.

2. **Fallback**: Yahoo Finance (if Alpha Vantage fails)
   - Uses original format IRFC.NS
   - Returns same data structure

### For US Stocks (e.g., AAPL, MSFT)
1. **First Try**: Finnhub (60 calls/min, free)
   - Best for US markets
   - Real-time data

2. **Second Try**: Alpha Vantage (if Finnhub fails)
   - 25 calls/day limit
   - Good global coverage

3. **Third Try**: Yahoo Finance (final fallback)
   - Always available
   - Unlimited calls via proxy

## Expected Console Output

### Successful Fetch:
```
[MarketData] 🔍 Fetching IRFC.NS...
[AlphaVantage] 🔍 Fetching IRFC.BSE...
[AlphaVantage] 📥 Response for IRFC.BSE: {...}
[AlphaVantage] ✅ Success for IRFC.NS: {
  symbol: "IRFC.NS",
  price: 170.50,
  change: 5.30,
  changePercent: 3.21,
  volume: 45678900,
  high: 172.00,
  low: 168.50,
  open: 169.00,
  previousClose: 165.20,
  lastUpdated: "2026-01-31T...",
  companyName: "IRFC.NS",
  exchange: "NSE"
}
```

### Fallback in Action:
```
[MarketData] 🔍 Fetching AAPL...
[Finnhub] 🔍 Fetching AAPL...
[Finnhub] ❌ Error for AAPL: Some error
[Finnhub] ⚠️ Failed for AAPL, trying Alpha Vantage...
[AlphaVantage] 🔍 Fetching AAPL...
[AlphaVantage] ✅ Success for AAPL: {...}
```

## Common Issues & Solutions

### Issue: "Alpha Vantage API limit reached"
**Solution**: System will automatically use Yahoo Finance fallback
**Prevention**: Prices are cached for 60 seconds

### Issue: "Symbol not found"
**Solution**: Ensure Indian stocks use .NS or .BO suffix
- ✅ Correct: `RELIANCE.NS`, `IRFC.NS`
- ❌ Wrong: `RELIANCE`, `IRFC`

### Issue: All APIs failing
**Check**:
1. Internet connection
2. API keys in environment.ts
3. Proxy configuration in proxy.conf.json

## Rate Limits (Free Tier)

| Provider | Limit | What Happens When Exceeded |
|----------|-------|---------------------------|
| Alpha Vantage | 25/day | Automatic fallback to Yahoo |
| Finnhub | 60/min | Automatic fallback to Alpha Vantage |
| Yahoo Finance | Unlimited* | No fallback needed |

*Via proxy, no documented limits

## Cache Behavior

- Quotes are cached for **60 seconds**
- Reduces API calls significantly
- Cache clears on page refresh
- Manual clear: `service.clearCache()`

## Auto-Refresh

If enabled in your component:
- Prices refresh every **2 minutes** (configurable)
- Uses cached data when available
- Respects rate limits with delays

## Verifying API Keys

Check if your keys are working:

### Alpha Vantage:
```bash
curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=RELIANCE.BSE&apikey=YOUR_KEY"
```

### Finnhub:
```bash
curl "https://finnhub.io/api/v1/quote?symbol=AAPL&token=YOUR_KEY"
```

## Success Indicators

You'll know everything is working when:
1. ✅ Console shows provider initialization
2. ✅ Stock prices appear on portfolio page
3. ✅ Prices update without errors
4. ✅ Change % and colors (green/red) display correctly
5. ✅ Multiple stocks load successfully

## Performance Optimization

Current settings in your service:
- **Cache Duration**: 60 seconds (reduces API calls)
- **Batch Delay**: 300ms between requests (prevents rate limiting)
- **Request Timeout**: 10-15 seconds per provider
- **Auto-fallback**: Immediate on provider failure

## Next Steps

1. **Test the application** - Load portfolio page
2. **Monitor console** - Watch for successful fetches
3. **Add more stocks** - Test with various Indian/US symbols
4. **Check performance** - Ensure smooth updates

## API Keys Status

✅ **Alpha Vantage**: Configured (`9T8D85D3AQIQ8VO2`)
✅ **Finnhub**: Configured (`d5dpe71r01qur4itoq3gd5dpe71r01qur4itoq40`)
✅ **Yahoo Finance**: No key needed (proxy-based)

## Summary

Your application now has:
- ✅ **3-tier fallback system** for maximum reliability
- ✅ **Smart provider selection** based on stock type
- ✅ **Rate limit protection** with caching and delays  
- ✅ **Automatic retries** with different providers
- ✅ **Real-time updates** for both Indian and US markets

**No additional API keys needed** - Your current setup is complete and production-ready for development!
