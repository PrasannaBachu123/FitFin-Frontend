# Finnhub API Limitations - Important Information

## 🔒 Current Issue: Indian Stocks Not Available

### The Problem
Your Finnhub API key is on the **FREE TIER**, which **ONLY SUPPORTS US STOCKS**.

When you try to fetch Indian stocks like HCLTECH, you get:
```
{"error":"You don't have access to this resource."}
```

### What Works ✅
**US Stocks** (Free tier includes):
- AAPL (Apple)
- GOOGL (Google/Alphabet)
- MSFT (Microsoft)
- TSLA (Tesla)
- NVDA (Nvidia)
- AMZN (Amazon)
- META (Meta/Facebook)
- And all other US stocks

### What Doesn't Work ❌
**Indian Stocks** (Requires paid plan):
- HCLTECH.NS
- RELIANCE.NS
- TCS.NS
- INFY.NS
- Any NSE/BSE stocks

## 💡 Solutions

### Option 1: Use US Stocks Only (FREE)
**Recommended for testing:**
- Simply use US stock symbols in your portfolio
- Works immediately with your current free API key
- Examples: AAPL, GOOGL, MSFT, TSLA, NVDA

### Option 2: Upgrade Finnhub Plan (PAID)
**For Indian Stock Support:**
1. Visit: https://finnhub.io/pricing
2. Choose a paid plan (starts around $9.99/month)
3. Get access to:
   - Indian stocks (NSE/BSE)
   - More API calls per minute
   - Additional features

### Option 3: Switch to Alpha Vantage API (FREE)
**Best for Indian Stocks:**

Alpha Vantage offers free API access to Indian stocks:
1. Sign up: https://www.alphavantage.co/support/#api-key
2. Free tier includes:
   - Indian NSE stocks
   - 25 API calls per day (500/day with free key)
   - Global stock data

**Implementation Required:**
- Update `market-data.service.ts` to use Alpha Vantage API
- Different API endpoint format
- Need to handle rate limits

### Option 4: Manual Entry (NO API)
**Immediate workaround:**
- Enter stock symbols without fetching live price
- Manually input current price in the form
- Update prices manually when needed

## 🧪 Testing with Current Setup

### Test with US Stocks (Will Work)
```
Symbol: AAPL
Expected: ✅ Live price fetched successfully
```

```
Symbol: GOOGL
Expected: ✅ Live price fetched successfully
```

### Test with Indian Stocks (Will Fail)
```
Symbol: HCLTECH or HCLTECH.NS
Expected: ❌ "You don't have access to this resource"
```

## 📊 API Response Examples

### US Stock (Success)
```json
{
  "c": 271.01,
  "d": -0.85,
  "dp": -0.3127,
  "h": 277.84,
  "l": 269,
  "o": 272.255,
  "pc": 271.86,
  "t": 1767387600
}
```

### Indian Stock (Access Denied)
```json
{
  "error": "You don't have access to this resource."
}
```

### Invalid Symbol (No Data)
```json
{
  "c": 0,
  "d": null,
  "dp": null,
  "h": 0,
  "l": 0,
  "o": 0,
  "pc": 0,
  "t": 0
}
```

## 🔧 Current Code Changes

The code has been updated to:

1. **Keep .NS suffix** for Indian stocks (Finnhub requires it)
2. **Better error messages** explaining the limitation
3. **Access denied detection** for paid-tier-only features
4. **Clear UI hints** showing "US stocks only (free tier)"

## 🎯 Recommended Next Steps

1. **For immediate testing:** Use US stocks like AAPL, MSFT, GOOGL
2. **For Indian stocks:** Consider Alpha Vantage API or Finnhub paid plan
3. **Temporary workaround:** Enter symbols and prices manually

## 📞 Support

- **Finnhub Support:** https://finnhub.io/support
- **Alpha Vantage Docs:** https://www.alphavantage.co/documentation/
- **Pricing Comparison:** Finnhub paid vs Alpha Vantage free

---

**Last Updated:** January 5, 2026
**Your API Key:** d5dpe71r01qur4itoq3g... (Free tier)
**Limitation:** US stocks only
