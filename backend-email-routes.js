/**
 * Express Backend Routes for Email Expense Fetching
 *
 * This file contains the backend API routes that integrate with the Python mail.py script
 * to fetch expenses from Gmail and import them into the database.
 *
 * Installation:
 * npm install child_process util
 *
 * Usage:
 * Add these routes to your Express app or import them in your main router file.
 */

const express = require('express');
const router = express.Router();
const { exec } = require('child_process');
const path = require('path');
const util = require('util');
const execPromise = util.promisify(exec);

// Import your authentication middleware
// const { authenticateToken } = require('../middleware/auth');

// Import your database models
// const Expense = require('../models/Expense');

/**
 * POST /api/expenses/fetch-from-email
 *
 * Fetches expense transactions from Gmail using the Python mail.py script
 *
 * Request Body:
 * {
 *   "emailCount": 10,     // Number of emails to fetch (1-50)
 *   "type": "debit"       // Transaction type: "debit" or "credit"
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "data": [
 *     {
 *       "creditor": "Merchant Name",
 *       "amount": "500",
 *       "date": "20-01-26",
 *       "utr": "224860703XXX"
 *     }
 *   ],
 *   "count": 5
 * }
 */
router.post('/fetch-from-email', async (req, res) => {
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
        message: 'Type must be either "debit" or "credit"'
      });
    }

    console.log(`[Email Fetch] Fetching ${emailCount} ${type} transactions from email`);

    // Determine Python executable
    const pythonExe = process.env.PYTHON_PATH || 'python3';

    // Path to your Python script
    // Adjust this path based on where your mail.py is located
    const pythonScriptPath = path.join(__dirname, '..', '..', 'mail.py');

    // Build command
    const pythonCommand = `${pythonExe} "${pythonScriptPath}" --noe ${emailCount} --${type}`;

    console.log(`[Email Fetch] Executing: ${pythonCommand}`);

    // Execute Python script with timeout
    const { stdout, stderr } = await execPromise(pythonCommand, {
      timeout: 120000,      // 2 minute timeout
      maxBuffer: 10 * 1024 * 1024,  // 10MB buffer
      env: {
        ...process.env,
        // Ensure Python can access .env variables
        PATH: process.env.PATH
      }
    });

    // Log any stderr output (warnings, etc.)
    if (stderr) {
      console.warn('[Email Fetch] Python stderr:', stderr);
    }

    console.log('[Email Fetch] Python stdout:', stdout);

    // Parse JSON output from Python script
    try {
      const transactions = JSON.parse(stdout);

      if (!Array.isArray(transactions)) {
        throw new Error('Python script did not return an array');
      }

      console.log(`[Email Fetch] Successfully fetched ${transactions.length} transactions`);

      res.json({
        success: true,
        data: transactions,
        count: transactions.length,
        message: `Fetched ${transactions.length} transactions from email`
      });

    } catch (parseError) {
      console.error('[Email Fetch] Failed to parse Python output:', stdout);
      console.error('[Email Fetch] Parse error:', parseError);

      res.status(500).json({
        success: false,
        message: 'Failed to parse email data. The Python script may have returned invalid JSON.',
        error: parseError.message,
        output: stdout.substring(0, 500) // First 500 chars for debugging
      });
    }

  } catch (error) {
    console.error('[Email Fetch] Error:', error);

    // Check for specific error types
    if (error.killed) {
      return res.status(504).json({
        success: false,
        message: 'Email fetching timed out. Try reducing the email count.',
        error: 'Timeout'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to fetch emails from inbox',
      error: error.message,
      stderr: error.stderr
    });
  }
});

module.exports = router;

/* ========== INTEGRATION INSTRUCTIONS ========== */

/**
 * To integrate this route into your Express app:
 *
 * 1. Save this file as: backend/routes/emailExpenses.js
 *
 * 2. In your main app file (app.js or server.js), add:
 *
 *    const emailExpensesRouter = require('./routes/emailExpenses');
 *    app.use('/api/expenses', emailExpensesRouter);
 *
 * 3. Ensure you have authentication middleware applied:
 *
 *    const { authenticateToken } = require('./middleware/auth');
 *    router.use(authenticateToken); // Add at top of this file
 *
 * 4. Frontend will use the existing POST /api/expenses endpoint to save transactions
 *    No additional database logic needed in this file!
 *
 * 5. Configure .env file with:
 *
 *    PYTHON_PATH=python3
 *    GMAIL_USER=your-email@gmail.com
 *    GMAIL_APP_PASSWORD=your-16-char-app-password
 *
 * 6. Test the endpoint:
 *
 *    curl -X POST http://localhost:5000/api/expenses/fetch-from-email \
 *      -H "Authorization: Bearer YOUR_TOKEN" \
 *      -H "Content-Type: application/json" \
 *      -d '{"emailCount": 10, "type": "credit"}'
 *
 * 7. Frontend will then call your existing POST /api/expenses endpoint
 *    for each transaction to save them individually.
 */
