# CORS Fix for Yahoo Finance API

## Problem
The error "Unable to fetch price for HCLTECH.NS" was occurring even with correct symbol format because:

**Yahoo Finance API blocks direct browser requests due to CORS (Cross-Origin Resource Sharing) restrictions.**

## What is CORS?
CORS is a security feature that prevents websites from making requests to different domains. Yahoo Finance API doesn't allow direct calls from browser JavaScript for security reasons.

## Solution Implemented: CORS Proxy

### ✅ Quick Fix (Development)
Added a CORS proxy service that acts as an intermediary:

```
Browser → CORS Proxy → Yahoo Finance API → CORS Proxy → Browser
```

**CORS Proxy Used:** `https://corsproxy.io/`
- Free service
- No setup required
- Works immediately
- Good for development/testing

### How It Works:
```typescript
// Before (Blocked by CORS):
const url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=HCLTECH.NS';

// After (Works with CORS Proxy):
const url = 'https://corsproxy.io/?https%3A%2F%2Fquery1.finance.yahoo.com%2Fv7%2Ffinance%2Fquote%3Fsymbols%3DHCLTECH.NS';
```

## Configuration

### Environment Settings
File: `src/environments/environment.ts`

```typescript
export const environment = {
  marketData: {
    // CORS proxy URL - change this based on your needs
    corsProxy: 'https://corsproxy.io/?',
    
    // Alternative proxies you can try:
    // corsProxy: 'https://api.allorigins.win/raw?url=',
    // corsProxy: 'https://corsproxy.org/?',
    // corsProxy: '', // Empty = direct call (needs backend proxy)
    
    cacheTimeout: 60000,        // 1 minute
    autoRefreshInterval: 120000  // 2 minutes
  }
};
```

### Switching CORS Proxies
If one proxy is slow or down, try these alternatives in `environment.ts`:

1. **corsproxy.io** (Current)
   ```typescript
   corsProxy: 'https://corsproxy.io/?'
   ```

2. **AllOrigins**
   ```typescript
   corsProxy: 'https://api.allorigins.win/raw?url='
   ```

3. **CORS Anywhere** (requires deployment)
   ```typescript
   corsProxy: 'https://cors-anywhere.herokuapp.com/'
   ```

4. **No Proxy** (backend required)
   ```typescript
   corsProxy: ''
   ```

## Testing the Fix

### Test Case 1: HCL Technologies
1. Open Add Investment modal
2. Enter symbol: `HCLTECH.NS`
3. Click 🔄 refresh button
4. **Expected:** Success! Shows live price ~₹1,607.60
5. **Expected:** Displays "HCL Technologies Ltd"

### Test Case 2: Other Indian Stocks
Try these symbols:
- `RELIANCE.NS` - Reliance Industries
- `TCS.NS` - Tata Consultancy Services
- `INFY.NS` - Infosys
- `SBIN.NS` - State Bank of India

All should now work correctly!

## Production Considerations

### ⚠️ Important: CORS Proxies for Production

**DO NOT use public CORS proxies in production!**

Reasons:
- Rate limits
- Unreliable uptime
- Potential security risks
- Slower performance
- No SLA/support

### Recommended Production Solutions:

#### Option 1: Backend Proxy (Best)
Create your own backend endpoint:

```javascript
// Node.js/Express Example
app.get('/api/stock-quote/:symbol', async (req, res) => {
  const symbol = req.params.symbol;
  const url = `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbol}`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch stock data' });
  }
});
```

Then update Angular service:
```typescript
// Instead of Yahoo API directly, call your backend
const url = `${environment.apiUrl}/stock-quote/${symbol}`;
```

#### Option 2: Deploy Your Own CORS Proxy
1. Clone: https://github.com/Rob--W/cors-anywhere
2. Deploy to Heroku/Vercel/AWS
3. Use your own proxy URL

#### Option 3: Use Paid APIs with CORS Support
- **Alpha Vantage** - Free tier available
- **Finnhub** - 60 API calls/minute free
- **IEX Cloud** - 50,000 messages/month free
- **Polygon.io** - Good for US markets

## Alternative: Native Fetch with Backend

### Backend Implementation (Python/Flask)
```python
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    url = f'https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}'
    response = requests.get(url)
    return jsonify(response.json())
```

### Update Angular Service
```typescript
getQuote(symbol: string): Observable<StockQuote> {
  // Call your backend instead of Yahoo directly
  const url = `${environment.apiUrl}/stock/${symbol}`;
  return this.http.get<any>(url).pipe(...);
}
```

## Troubleshooting

### Issue: Still getting CORS errors
**Solution:**
1. Clear browser cache
2. Check browser console for exact error
3. Try alternative CORS proxy
4. Verify internet connection

### Issue: Slow response times
**Solution:**
1. The CORS proxy adds latency (500ms-2s)
2. Try different proxy service
3. Implement caching (already included)
4. Consider backend proxy

### Issue: Rate limiting
**Solution:**
1. Public proxies may have rate limits
2. Implement request throttling
3. Use backend proxy
4. Switch to paid API

## Files Modified

1. **market-data.service.ts**
   - Added CORS proxy support
   - Uses environment configuration
   - Wraps all API calls with proxy

2. **environment.ts**
   - Added `marketData` configuration
   - Configurable CORS proxy
   - Cache and refresh settings

## Testing Checklist

- [x] HCLTECH.NS fetches correct price
- [x] No CORS errors in browser console
- [x] Price displays in investment modal
- [x] Multiple symbols work in refresh
- [x] Watchlist loads live prices
- [x] Search functionality works
- [x] Cache prevents duplicate requests

## Status

✅ **CORS Issue RESOLVED**  
✅ **Live prices now working**  
✅ **All Indian stocks supported**  
✅ **Configurable proxy settings**  

⚠️ **Note:** Remember to implement backend proxy for production!

---

**Updated:** January 5, 2026  
**Status:** Working in Development  
**Production Ready:** Requires backend proxy
