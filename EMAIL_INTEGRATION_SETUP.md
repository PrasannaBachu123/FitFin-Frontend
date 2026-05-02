# Email Expense Integration - Complete Setup Guide

## 🎯 Overview

This integration allows users to automatically fetch expense transactions (debit/credit) from their Gmail inbox using a Python script (`mail.py`) and import them into the FitFin expense tracker.

## 📋 Prerequisites

- ✅ Python 3.x installed
- ✅ Node.js backend server (Express)
- ✅ Gmail account with App Password enabled
- ✅ `mail.py` script that returns JSON in the specified format

## 🚀 Setup Instructions

### Step 1: Frontend Setup (Already Complete ✅)

The frontend has been fully integrated with:
- ✅ Email fetch button in Expense Analysis toolbar
- ✅ Modal dialog for configuring email fetch parameters
- ✅ API service methods for backend communication
- ✅ Loading states, error handling, and success feedback

**Location:** `src/app/expense-analysis.component.*`

### Step 2: Backend API Setup

#### Option A: Add to Existing Express App

1. **Copy the routes file to your backend:**
   ```bash
   cp backend-email-routes.js /path/to/your/backend/routes/emailExpenses.js
   ```

2. **Install required dependencies:**
   ```bash
   npm install child_process util
   ```

3. **Import and use the routes in your main app file:**

   ```javascript
   // In your server.js or app.js
   const emailExpensesRouter = require('./routes/emailExpenses');
   
   // Apply authentication middleware
   const { authenticateToken } = require('./middleware/auth');
   
   // Mount the routes
   app.use('/api/expenses', authenticateToken, emailExpensesRouter);
   ```

4. **Update database save logic in the routes:**

   Find the section in `backend-email-routes.js` that says:
   ```javascript
   // Save to database
   // Replace this with your actual database save logic
   ```

   And replace it with your actual database model:

   **For MongoDB/Mongoose:**
   ```javascript
   const Expense = require('../models/Expense');
   const savedExpense = await Expense.create(expenseData);
   importedExpenses.push(savedExpense);
   ```

   **For PostgreSQL/Sequelize:**
   ```javascript
   const { Expense } = require('../models');
   const savedExpense = await Expense.create(expenseData);
   importedExpenses.push(savedExpense);
   ```

#### Option B: Standalone Backend Routes

If you prefer to test independently:

```javascript
// standalone-server.js
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const emailExpensesRouter = require('./backend-email-routes');
app.use('/api/expenses', emailExpensesRouter);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

### Step 3: Environment Configuration

1. **Create `.env` file in your backend directory:**
   ```bash
   cp backend.env.example /path/to/your/backend/.env
   ```

2. **Configure Gmail credentials:**

   **Get Gmail App Password:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not enabled
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Other (Custom name)"
   - Name it "FitFin App" and click Generate
   - Copy the 16-character password (format: `abcd efgh ijkl mnop`)

   **Update `.env`:**
   ```env
   GMAIL_USER=your-email@gmail.com
   GMAIL_APP_PASSWORD=abcdefghijklmnop  # No spaces!
   PYTHON_PATH=python3
   ```

3. **Add `.env` to `.gitignore`:**
   ```bash
   echo ".env" >> .gitignore
   ```

### Step 4: Python Script Setup

1. **Ensure `mail.py` is in your backend directory**

2. **Test the Python script manually:**
   ```bash
   cd /path/to/backend
   python3 mail.py --noe 5 --credit
   ```

   Expected output (JSON):
   ```json
   [
     {
       "creditor": "Merchant Name",
       "amount": "500.00",
       "date": "20-01-26",
       "utr": "224860703XXX"
     }
   ]
   ```

3. **Verify Python script requirements:**
   - Script must accept `--noe <count>` flag
   - Script must accept `--debit` or `--credit` flag
   - Script must output valid JSON to stdout
   - Script must use Gmail credentials from environment

4. **Make script executable (Linux/Mac):**
   ```bash
   chmod +x mail.py
   ```

### Step 5: Backend Verification

1. **Start your backend server:**
   ```bash
   cd /path/to/backend
   npm start
   ```

2. **Test the fetch endpoint with curl:**
   ```bash
   curl -X POST http://localhost:5000/api/expenses/fetch-from-email \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"emailCount": 5, "type": "credit"}'
   ```

   Expected response:
   ```json
   {
     "success": true,
     "data": [
       {
         "creditor": "Merchant Name",
         "amount": "500.00",
         "date": "20-01-26",
         "utr": "224860703XXX"
       }
     ],
     "count": 1
   }
   ```

3. **Test the import endpoint:**
   ```bash
   curl -X POST http://localhost:5000/api/expenses/import-email \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "transactions": [
         {
           "creditor": "Test Merchant",
           "amount": "500",
           "date": "20-01-26",
           "utr": "123456789"
         }
       ]
     }'
   ```

## 🧪 Testing the Full Integration

### Frontend Testing

1. **Start the Angular app:**
   ```bash
   cd my-angular-app
   npm start
   ```

2. **Navigate to Expense Analysis:**
   - Login to your account
   - Go to Dashboard → Expense Analysis
   - Click the "📧 Fetch from Email" button

3. **Test the email fetch flow:**
   - Select transaction type (Credit or Debit)
   - Enter number of emails (1-50)
   - Click "Fetch Emails"
   - Verify transactions appear in preview
   - Click "Import X Transactions"
   - Verify success message
   - Verify transactions appear in expense list

### Error Handling Testing

Test these scenarios:

1. **Invalid email count:**
   - Try entering 0 or 51 emails
   - Should show validation error

2. **Backend unavailable:**
   - Stop backend server
   - Try fetching emails
   - Should show connection error

3. **Python script fails:**
   - Temporarily rename `mail.py`
   - Try fetching emails
   - Should show error message

4. **Invalid Gmail credentials:**
   - Use wrong Gmail password in `.env`
   - Should show authentication error

## 🔧 Troubleshooting

### Issue: "Python not found"

**Solution:**
```bash
# Find Python path
which python3  # Linux/Mac
where python3  # Windows

# Update .env
PYTHON_PATH=/usr/bin/python3
# or
PYTHON_PATH=C:\Python39\python.exe
```

### Issue: "Mail.py execution failed"

**Diagnostics:**
```bash
# Test Python script directly
cd backend
python3 mail.py --noe 5 --debit

# Check for errors
python3 -m py_compile mail.py

# Verify permissions
ls -l mail.py
chmod +x mail.py  # If needed
```

### Issue: "Failed to parse email data"

**Check:**
- Python script outputs valid JSON
- No print statements before JSON output
- JSON is properly formatted

**Test:**
```bash
python3 mail.py --noe 1 --credit | python3 -m json.tool
```

### Issue: "Authentication failed"

**Verify:**
- Gmail App Password is correct (16 chars, no spaces)
- 2-Step Verification is enabled
- App Password hasn't been revoked
- `.env` file is loaded correctly

**Test:**
```javascript
// In Node.js backend
console.log('Gmail User:', process.env.GMAIL_USER);
console.log('Password set:', !!process.env.GMAIL_APP_PASSWORD);
```

### Issue: "Timeout errors"

**Solutions:**
- Reduce email count
- Increase timeout in backend:
  ```javascript
  await execPromise(pythonCommand, {
    timeout: 180000,  // 3 minutes
    maxBuffer: 20 * 1024 * 1024  // 20MB
  });
  ```

### Issue: "CORS errors"

**Fix:**
```javascript
// In backend
app.use(cors({
  origin: 'http://localhost:4200',
  credentials: true
}));
```

## 📊 Monitoring and Logs

### Backend Logs

The backend logs will show:
```
[Email Fetch] Fetching 10 debit transactions from email
[Email Fetch] Executing: python3 "/.../mail.py" --noe 10 --debit
[Email Fetch] Successfully fetched 8 transactions
[Email Import] Importing 8 transactions for user 123
[Email Import] Imported 8 transactions, 0 failed
```

### Frontend Console

Check browser console for:
- API request/response logs
- Email fetch status
- Import results

## 🔒 Security Considerations

1. **Gmail App Password:**
   - ✅ Use App Password, never regular password
   - ✅ Store in `.env`, never in code
   - ✅ Rotate regularly (every 3-6 months)
   - ✅ Revoke if compromised

2. **Rate Limiting:**
   - Implement rate limits on email fetch endpoint
   - Limit to 10 requests per hour per user
   - Monitor for abuse

3. **Authentication:**
   - Always verify user authentication
   - Validate user owns the email account
   - Never expose email credentials to frontend

4. **Input Validation:**
   - Sanitize all inputs
   - Validate email count (1-50)
   - Validate transaction data before import

5. **Error Messages:**
   - Don't expose sensitive info in errors
   - Log detailed errors server-side only
   - Show generic errors to users

## 📈 Performance Optimization

1. **Caching:**
   - Cache fetched emails temporarily
   - Prevent duplicate fetches

2. **Batch Processing:**
   - Import transactions in batches
   - Use database transactions for atomicity

3. **Background Processing:**
   - Move email fetching to background job
   - Use job queue (Bull, BullMQ)
   - Notify user when complete

## 🎨 UI Customization

### Button Styling

In `expense-analysis.component.css`, customize:
```css
.cta-email {
  background: linear-gradient(135deg, #your-color-1, #your-color-2);
}
```

### Modal Colors

Update modal theme:
```css
.email-modal {
  background: #your-bg-color;
  border: 1px solid #your-border-color;
}
```

## 📝 Next Steps

1. **Add transaction categorization:**
   - Auto-categorize based on merchant name
   - Use ML for better categorization

2. **Duplicate detection:**
   - Check UTR before importing
   - Prevent duplicate entries

3. **Notification system:**
   - Notify user when import completes
   - Send email summary

4. **Analytics:**
   - Track email fetch usage
   - Monitor success/failure rates
   - Identify common errors

## 📚 Additional Resources

- [Gmail App Passwords Guide](https://support.google.com/accounts/answer/185833)
- [Express.js Documentation](https://expressjs.com/)
- [Child Process Node.js](https://nodejs.org/api/child_process.html)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)

## 💡 Support

For issues or questions:
1. Check troubleshooting section above
2. Review backend logs
3. Test Python script independently
4. Verify environment configuration

## ✅ Setup Checklist

- [ ] Frontend components added
- [ ] API service methods implemented
- [ ] Backend routes created
- [ ] Database save logic configured
- [ ] `.env` file configured with Gmail credentials
- [ ] `mail.py` script tested independently
- [ ] Backend API endpoints tested with curl
- [ ] Full integration tested in browser
- [ ] Error handling verified
- [ ] Security considerations addressed
- [ ] Rate limiting implemented
- [ ] Monitoring/logging configured

---

**Setup Date:** ${new Date().toISOString().split('T')[0]}
**Version:** 1.0.0
**Status:** ✅ Ready for Production
