# Backend Email Integration Guide

## Overview
This guide explains how to integrate the Python email fetching script with your backend API.

## Prerequisites
- Python 3.x installed
- `mail.py` script in your backend directory
- App password stored in `.env` file
- Node.js backend server

## Backend API Endpoint

Add the following route to your Express backend (usually in `routes/expenses.js` or `server.js`):

```javascript
const { exec } = require('child_process');
const path = require('path');
const util = require('util');
const execPromise = util.promisify(exec);

// POST /api/expenses/fetch-from-email
router.post('/fetch-from-email', authenticateToken, async (req, res) => {
  try {
    const { emailCount = 10, type = 'debit' } = req.body;
    
    // Validate inputs
    if (emailCount < 1 || emailCount > 50) {
      return res.status(400).json({ 
        success: false, 
        message: 'Email count must be between 1 and 50' 
      });
    }
    
    if (!['debit', 'credit'].includes(type)) {
      return res.status(400).json({ 
        success: false, 
        message: 'Type must be either debit or credit' 
      });
    }
    
    // Path to your Python script (adjust as needed)
    const pythonScriptPath = path.join(__dirname, '..', 'mail.py');
    const pythonCommand = `python3 "${pythonScriptPath}" --noe ${emailCount} --${type}`;
    
    console.log(`Executing: ${pythonCommand}`);
    
    // Execute Python script
    const { stdout, stderr } = await execPromise(pythonCommand, {
      timeout: 60000, // 60 second timeout
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    });
    
    if (stderr) {
      console.error('Python script stderr:', stderr);
    }
    
    // Parse JSON output from Python script
    try {
      const transactions = JSON.parse(stdout);
      
      console.log(`Fetched ${transactions.length} transactions from email`);
      
      res.json({
        success: true,
        data: transactions,
        count: transactions.length
      });
    } catch (parseError) {
      console.error('Failed to parse Python output:', stdout);
      res.status(500).json({
        success: false,
        message: 'Failed to parse email data',
        error: parseError.message
      });
    }
    
  } catch (error) {
    console.error('Error fetching emails:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch emails from inbox',
      error: error.message
    });
  }
});

// POST /api/expenses/import-email
router.post('/import-email', authenticateToken, async (req, res) => {
  try {
    const { transactions } = req.body;
    const userId = req.user.id;
    
    if (!Array.isArray(transactions) || transactions.length === 0) {
      return res.status(400).json({ 
        success: false, 
        message: 'No transactions provided' 
      });
    }
    
    const importedExpenses = [];
    const errors = [];
    
    for (const txn of transactions) {
      try {
        // Map email transaction to expense format
        const expense = {
          userId: userId,
          title: txn.creditor || 'Email Transaction',
          amount: parseFloat(txn.amount) || 0,
          category: 'Uncategorized', // User can update later
          date: parseDate(txn.date), // Convert DD-MM-YY to Date
          notes: `UTR: ${txn.utr}`,
          type: 'debit', // or determine from context
          paymentMethod: 'UPI',
          source: 'email',
          passThrough: false
        };
        
        // Save to database (adjust according to your DB schema)
        const savedExpense = await Expense.create(expense);
        importedExpenses.push(savedExpense);
        
      } catch (error) {
        console.error('Error importing transaction:', txn, error);
        errors.push({ transaction: txn, error: error.message });
      }
    }
    
    res.json({
      success: true,
      message: `Successfully imported ${importedExpenses.length} transactions`,
      data: {
        imported: importedExpenses.length,
        failed: errors.length,
        errors: errors
      }
    });
    
  } catch (error) {
    console.error('Error importing email expenses:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to import email expenses',
      error: error.message
    });
  }
});

// Helper function to parse DD-MM-YY date format
function parseDate(dateStr) {
  // Input format: "20-01-26" (DD-MM-YY)
  const [day, month, year] = dateStr.split('-');
  const fullYear = `20${year}`; // Assuming 20xx
  return new Date(`${fullYear}-${month}-${day}`);
}

module.exports = router;
```

## Environment Variables (.env)

Add these to your backend `.env` file:

```env
# Gmail Configuration
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password
PYTHON_PATH=python3
```

## Python Script Location

Ensure your `mail.py` script is in the backend directory and has the following structure:

```python
# mail.py
# Expected output format:
[
  {
    "creditor": "XXX XXXX XXXX",
    "amount": "9XX",
    "date": "20-01-26",
    "utr": "224860703XXX"
  }
]
```

## Testing

Test the endpoint with curl or Postman:

```bash
curl -X POST http://localhost:5000/api/expenses/fetch-from-email \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"emailCount": 10, "type": "credit"}'
```

## Error Handling

The backend will handle:
- Invalid email counts (must be 1-50)
- Invalid types (must be debit or credit)
- Python script execution errors
- JSON parsing errors
- Database insertion errors

## Security Notes

1. **Never commit** your `.env` file with app password
2. Use app-specific passwords, not your main Gmail password
3. Validate and sanitize all inputs
4. Implement rate limiting on this endpoint
5. Ensure proper authentication middleware

## Troubleshooting

### Python not found
- Set `PYTHON_PATH` in .env to full path: `/usr/bin/python3`
- On Windows: `C:\\Python39\\python.exe`

### Mail.py execution fails
- Check Python script has executable permissions: `chmod +x mail.py`
- Test script manually: `python3 mail.py --noe 5 --credit`
- Check .env variables are loaded correctly

### Timeout errors
- Increase timeout in execPromise options
- Reduce `emailCount` parameter
- Check email server connectivity

## Integration Checklist

- [ ] Backend route added to Express app
- [ ] `.env` file configured with Gmail credentials
- [ ] `mail.py` script placed in backend directory
- [ ] Authentication middleware applied to routes
- [ ] Database schema supports email-imported transactions
- [ ] Frontend connected to new API endpoints
- [ ] Error handling tested
- [ ] Rate limiting configured
