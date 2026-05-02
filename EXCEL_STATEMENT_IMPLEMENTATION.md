# Excel Bank Statement Processing Implementation Guide

## Overview
This document describes the implementation of Excel bank statement processing with proper sign conventions, auto-categorization, and column mapping for the FitFin application.

## Sign Convention (CRITICAL)

### Amount Sign Rules
- **DEBITS/WITHDRAWALS**: Stored as **NEGATIVE** values
  - Example: Food payment of ₹80 → stored as `-80`
  - Category: Automatically set to an expense category (Food & Dining, etc.)
  
- **CREDITS/DEPOSITS**: Stored as **POSITIVE** values
  - Example: Salary of ₹29,500 → stored as `+29500`
  - Category: Automatically set to an income category (Salary, Interest, etc.)

### Calculation Example
```
Net Balance = Credits (Income) + Debits (Expenses)
            = +29500 + (-80) + (-1200) + (-500)
            = 29500 - 80 - 1200 - 500
            = 27720
```

## Frontend Implementation

### Location
`src/app/add-expense.component.ts` - Main component handling Excel processing

### Key Methods

#### 1. `extractAmountFromRow(row)`
**Purpose**: Extract and apply sign convention to amounts

**Logic**:
- Look for explicit Debit/Withdrawal columns → Return as **NEGATIVE**
- Look for explicit Credit/Deposit columns → Return as **POSITIVE**
- Fallback to generic "Amount" column → Return as-is (preserves original sign)

**Example**:
```typescript
// Debit column found with value 80
withdrawVal = 80
return -Math.abs(withdrawVal)  // Returns -80

// Credit column found with value 29500
depositVal = 29500
return +Math.abs(depositVal)   // Returns +29500
```

#### 2. `autoCategorizeTransaction(narration, amount)`
**Purpose**: Automatically categorize transactions based on narration text and direction

**Income Categories** (amount > 0):
- **Salary**: salary, wage, HCL, TCS, Infosys, payroll, NEFT CR
- **Interest**: interest, FD, fixed deposit
- **Refunds**: refund, reversal, merchant refund
- **Transfer In**: NEFT, IMPS, RTGS, transfer, credit, deposit
- **Others**: Any other credit

**Expense Categories** (amount < 0):
- **Food & Dining**: BharatPe, PayTM, Swiggy, Zomato, restaurant, cafe
- **Transportation**: APSRTC, Uber, Ola, bus, metro, fuel, parking
- **Groceries**: DMart, Reliance Fresh, BigBasket, supermarket
- **Shopping**: Amazon, Flipkart, Myntra, mall
- **Entertainment**: Netflix, movie, gaming, Spotify
- **Healthcare**: hospital, pharmacy, medicine, medical
- **Utilities**: electricity, water, gas, internet, mobile recharge
- **Education**: school, college, course, training
- **Personal Care**: salon, gym, fitness, spa
- **Others**: Unmatched transactions

#### 3. `findKeyBySubstring(source, substrings)`
**Purpose**: Intelligently locate columns in Excel file

**Column Detection Priority**:
1. **Exact match first** (e.g., "narration" == "narration")
2. **Substring match second** (e.g., "transaction narration" contains "narration")

**Supported Column Names**:

| Category | Variants |
|----------|----------|
| Date | Date, Txn Date, Transaction Date, Value Dt, Posting Date |
| Narration | Narration, Description, Details, Merchant, Particulars |
| Debit | Debit, Dr, Debit Amt, Withdrawal, Withdrawal Amt |
| Credit | Credit, Cr, Credit Amt, Deposit, Deposit Amt |
| Amount | Amount, Amt, Value, Transaction Amount |
| Type | Type, Dr/Cr, Transaction Type, Debit/Credit |

## Backend API Endpoints

### 1. Upload & Preview Statement
```http
POST /api/expenses/upload-statement
Content-Type: multipart/form-data

Field: file (or statement, document)
Type: Excel file (.xlsx, .xls)
Optional: password (string)

Response:
{
  "success": true,
  "data": [
    {
      "date": "2025-01-15",
      "narration": "HCL Technologies SALARY",
      "amount": 29500,          // POSITIVE for credit
      "category": "Salary",
      "paymentMethod": "Netbanking"
    },
    {
      "date": "2025-01-16",
      "narration": "Swiggy Food Order",
      "amount": -80,            // NEGATIVE for debit
      "category": "Food & Dining",
      "paymentMethod": "UPI"
    }
  ]
}
```

### 2. Bulk Create Expenses
```http
POST /api/expenses/bulk-create
Content-Type: application/json

{
  "transactions": [
    {
      "title": "HCL Technologies SALARY",
      "description": "HCL Technologies SALARY",
      "amount": 29500,
      "category": "Salary",
      "date": "2025-01-15",
      "paymentMethod": "Netbanking"
    },
    {
      "title": "Swiggy Food Order",
      "description": "Swiggy Food Order",
      "amount": -80,
      "category": "Food & Dining",
      "date": "2025-01-16",
      "paymentMethod": "UPI"
    }
  ]
}

Response:
{
  "success": true,
  "count": 2,
  "created": 2,
  "failed": 0,
  "summary": {
    "totalDebits": -80,
    "totalCredits": 29500,
    "netChange": 29420
  }
}
```

### 3. Direct Upload & Create
```http
POST /api/expenses/upload-and-create
Content-Type: multipart/form-data

Field: file (Excel file)
Optional: password

Response: Same as bulk-create
```

## Data Flow

### Processing Pipeline
```
User Selects Excel File
         ↓
parseExcelFile()
         ↓
mapExcelRowToTransaction()
  ├─ extractAmountFromRow() → Apply sign convention
  ├─ autoCategorizeTransaction() → Auto-categorize
  └─ Normalize date & payment method
         ↓
Filter out invalid rows (amount = 0)
         ↓
Preview Mode:
  ├─ Display transactions to user
  └─ User confirms before creating
         ↓
bulkCreateFromTransactions()
         ↓
API: POST /expenses/bulk-create
         ↓
Backend: Store with sign convention
         ↓
Frontend: Navigate to expense dashboard
```

## Testing Checklist

### 1. Amount Sign Convention
- [ ] Debit transactions stored as negative values
- [ ] Credit transactions stored as positive values
- [ ] Net balance calculation: Income - Expenses = Net
- [ ] Amount column without Debit/Credit variants preserves original sign

### 2. Auto-Categorization
- [ ] Salary narration → "Salary" category (income)
- [ ] Swiggy narration → "Food & Dining" category (expense)
- [ ] Amazon narration → "Shopping" category (expense)
- [ ] Interest narration → "Interest" category (income)
- [ ] Unknown transactions → "Others" category

### 3. Column Mapping
- [ ] Standard columns detected (Date, Narration, Debit, Credit)
- [ ] Alternate column names recognized
- [ ] Mixed case/spacing handled correctly
- [ ] Unknown columns skipped gracefully

### 4. File Upload
- [ ] Excel files (.xlsx, .xls) accepted
- [ ] CSV files accepted (if supported)
- [ ] Invalid file types rejected
- [ ] Preview shows correct number of rows
- [ ] Bulk create succeeds with multiple transactions

### 5. Payment Method Detection
- [ ] UPI keywords (upi, paytm, phonepe, googlepay) → "UPI"
- [ ] Card keywords (card, visa, mastercard) → "Card"
- [ ] Bank keywords (neft, imps, rtgs) → "Netbanking"
- [ ] Default fallback → "Cash"

## Example Excel File Format

| Date | Narration | Debit | Credit | Balance |
|------|-----------|-------|--------|---------|
| 2025-01-01 | Opening Balance | | 10000 | 10000 |
| 2025-01-15 | HCL Technologies SALARY CR | | 29500 | 39500 |
| 2025-01-16 | Swiggy Food Order | 80 | | 39420 |
| 2025-01-17 | Uber Ride | 150 | | 39270 |
| 2025-01-20 | Amazon Purchase | 5000 | | 34270 |
| 2025-01-21 | Bank Interest | | 50 | 34320 |

**Processing Results**:
- Opening Balance: `+10000` → Category: Others
- Salary: `+29500` → Category: Salary
- Swiggy: `-80` → Category: Food & Dining
- Uber: `-150` → Category: Transportation
- Amazon: `-5000` → Category: Shopping
- Interest: `+50` → Category: Interest

**Net Balance**: 39500 - 80 - 150 - 5000 + 50 = 34,320 ✓

## Backend Implementation Requirements

### Express/Node.js Controller Example
```javascript
// POST /api/expenses/bulk-create
app.post('/expenses/bulk-create', async (req, res) => {
  const { transactions } = req.body;
  
  try {
    // Validate sign convention
    const debits = transactions.filter(t => t.amount < 0);
    const credits = transactions.filter(t => t.amount > 0);
    
    console.log(`Processing ${debits.length} debits and ${credits.length} credits`);
    
    // Store with sign preservation
    const results = await Promise.all(
      transactions.map(t => 
        Expense.create({
          ...t,
          amount: t.amount,  // Preserve sign (negative for debits, positive for credits)
          userId: req.user.id,
          type: t.amount < 0 ? 'debit' : 'credit',
          createdAt: new Date(t.date)
        })
      )
    );
    
    res.json({
      success: true,
      count: results.length,
      created: results.length,
      summary: {
        totalDebits: debits.reduce((s, t) => s + t.amount, 0),
        totalCredits: credits.reduce((s, t) => s + t.amount, 0)
      }
    });
  } catch (error) {
    res.status(400).json({ success: false, error: error.message });
  }
});
```

## Troubleshooting

### Issue: "No valid transactions found"
**Causes**:
- Excel file has no numeric columns matching Amount/Debit/Credit patterns
- All amounts are zero or null
- Column names don't match expected patterns

**Solution**:
- Check browser console for column mapping logs
- Ensure Excel has columns: Date, Narration/Description, Amount or Debit/Credit
- Verify amounts are numeric (not text)

### Issue: Wrong categorization
**Causes**:
- Narration text doesn't match keywords
- Regex patterns need adjustment
- Amount sign affecting categorization logic

**Solution**:
- Extend `autoCategorizeTransaction()` with additional keywords
- Check narration text in console logs
- Verify amount sign (positive/negative) is correct

### Issue: Date parsing errors
**Causes**:
- Excel serial date format
- Non-standard date strings
- Missing date column

**Solution**:
- Excel dates are converted using: `(value - 25569) * 86400 * 1000`
- Supported formats: YYYY-MM-DD, MM/DD/YYYY, and Excel serial numbers
- Ensure at least one date column is present

## Future Enhancements

1. **Password-protected PDFs**: Support encrypted bank statements
2. **Multi-currency**: Handle different currency symbols and conversions
3. **Duplicate detection**: Prevent duplicate transaction uploads
4. **Manual categorization**: User override for auto-categories
5. **Recurring patterns**: Identify and tag recurring transactions
6. **Budget alerts**: Track spending against budgets
7. **Tax calculations**: Category-wise tax deduction summaries

## References

- [XLSX Library](https://sheetjs.com/) - Excel parsing
- [Angular FileReader API](https://developer.mozilla.org/en-US/docs/Web/API/FileReader)
- [HTTP MultipartFormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
