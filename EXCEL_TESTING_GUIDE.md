# Excel Bank Statement Testing Guide

## ✅ Changes Made to Fix Your Excel Format

### 1. **Column Name Detection Enhanced**
Your Excel has columns with dots like:
- `Withdrawal Amt.` → Now properly detected
- `Deposit Amt.` → Now properly detected
- `Value Dt.` → Now properly detected as date column
- `Chq./Ref.No.` → Now included in narration search

**Fix Applied**: 
- Added trailing dot removal in normalization: `replace(/\.$/, '')`
- Added 'withdrawal amt.' and 'deposit amt.' to search patterns
- Enhanced column detection with dots and special characters

### 2. **Date Format Parser Fixed**
Your dates are in **DD/MM/YY** format (e.g., `01/12/25`)

**Fix Applied**:
```typescript
// Now handles DD/MM/YY format correctly
01/12/25 → 2025-12-01
02/12/25 → 2025-12-02
```

### 3. **Enhanced Logging**
Added detailed console logs to help debug:
- Column names detected
- Sample row data
- Amount extraction details
- Mapped transaction preview

---

## 🧪 How to Test Your Excel File

### Step 1: Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Upload your Excel file
4. Look for these logs:

```
[Excel Parse] Total rows: 49
[Excel Parse] First row columns: ["Date", "Narration", "Chq./Ref.No.", "Value Dt", "Withdrawal Amt.", "Deposit Amt.", "Closing Balance"]
[Excel Parse] First row data: { Date: "01/12/25", Narration: "UPI-MEREEDU RAMBABU...", ... }
```

### Step 2: Verify Amount Detection
Look for logs like:
```
[Amount Extract] Found columns - withdraw key: "withdrawal amt" deposit key: "deposit amt"
[Amount Extract] Values - withdraw: 80 deposit: null
```

**Expected Results**:
- Withdrawals → **NEGATIVE** amounts (e.g., -80, -40, -10)
- Deposits → **POSITIVE** amounts (e.g., +29500)

### Step 3: Check Transaction Mapping
```
[Excel Parse] Row 1 mapped to: {
  title: "UPI-MEREEDU RAMBABU-BHARATPE...",
  amount: -80,
  category: "Food & Dining",
  date: "2025-12-01",
  paymentMethod: "UPI"
}
```

### Step 4: Verify Categorization

**Based on your sample data**:

| Narration | Expected Amount | Expected Category |
|-----------|----------------|-------------------|
| BHARATPE9H0Y7E2H9H381347 | -80 | Food & Dining |
| PAYTMQR6PHI1T | -40 | Food & Dining |
| BHARATPE09911880323 | -10 | Food & Dining |
| HCL TECHNOLOGIES LTD | +29500 | Salary |
| PAYTMQR6E46B2 | -25 | Food & Dining |
| LOKESHYALAMANCHILI46 | -30 | Others |
| APSRTC | -185 | Transportation |
| COFFE | -315 | Food & Dining |

---

## 🔍 What to Look For

### ✅ Correct Behavior:
1. **49 transactions parsed** (not more, not less)
2. **Debits show negative amounts**: -80, -40, -10, -25, -30, -185, -315
3. **Credits show positive amounts**: +29500
4. **Dates converted properly**: 01/12/25 → 2025-12-01
5. **Categories assigned automatically**:
   - UPI BharatPe/PayTM → Food & Dining
   - APSRTC → Transportation
   - HCL Technologies → Salary

### ❌ If Something is Wrong:

#### Problem: "No transactions found"
**Check Console for**:
```
[Excel Parse] Total rows: 0
```
**Fix**: Verify Excel has data, check if first row is headers

#### Problem: "All amounts are positive"
**Check Console for**:
```
[Amount Extract] Found columns - withdraw key: null deposit key: null
```
**Fix**: Column names don't match. Check exact column spelling in Excel

#### Problem: "Wrong dates"
**Check Console for**:
```
[Excel Parse] Row 1 mapped to: { date: "1970-01-01" }
```
**Fix**: Date parsing failed. Verify date format in Excel cells

#### Problem: "Wrong categories"
**Check Console for**:
```
[Excel Parse] Row 1 mapped to: { category: "Others" }
```
**Fix**: Narration keywords not matching. Check narration text

---

## 📊 Your Sample Data Expected Output

Based on your provided data:

```json
[
  {
    "title": "UPI-MEREEDU RAMBABU-BHARATPE9H0Y7E2H9H381347",
    "description": "UPI-MEREEDU RAMBABU-BHARATPE9H0Y7E2H9H381347@YESBANKLTD-YESB0YESUPI...",
    "amount": -80,
    "category": "Food & Dining",
    "date": "2025-12-01",
    "paymentMethod": "UPI"
  },
  {
    "title": "UPI-MUTHINENI SAI RAM-PAYTMQR6PHI1T",
    "description": "UPI-MUTHINENI SAI RAM-PAYTMQR6PHI1T@PTYS-YESB0PTMUPI...",
    "amount": -40,
    "category": "Food & Dining",
    "date": "2025-12-01",
    "paymentMethod": "UPI"
  },
  {
    "title": "NEFT CR-CITI0000002-HCL TECHNOLOGIES LTD",
    "description": "NEFT CR-CITI0000002-HCL TECHNOLOGIES LTD-LUCKNOW-MANJU NADH BATCHU...",
    "amount": 29500,
    "category": "Salary",
    "date": "2025-12-01",
    "paymentMethod": "Netbanking"
  },
  {
    "title": "UPI-APSRTC-APSRTCOFFLINEEPOS",
    "description": "UPI-APSRTC-APSRTCOFFLINEEPOS@AXL-UTIB0AXLUPI...",
    "amount": -185,
    "category": "Transportation",
    "date": "2025-12-02",
    "paymentMethod": "UPI"
  }
]
```

---

## 🚀 Testing Steps

1. **Save your Excel file** (make sure it has 49 rows of data)
2. **Reload the Angular app** (refresh browser)
3. **Open Developer Console** (F12 → Console tab)
4. **Navigate to Add Expense page**
5. **Click "Upload & Preview"**
6. **Select your Excel file**
7. **Check console logs** for the output shown above
8. **Verify preview table** shows correct data:
   - 49 transactions
   - Negative for debits
   - Positive for credits
   - Proper dates (2025-12-01, 2025-12-02, etc.)
   - Correct categories

---

## 💡 Tips

### Column Names in Your Excel:
Make sure your Excel has these exact columns:
- `Date` or `Value Dt`
- `Narration`
- `Withdrawal Amt.` (with or without the dot)
- `Deposit Amt.` (with or without the dot)

### If Categories are Wrong:
The auto-categorization looks for keywords in the narration:
- **BharatPe** → Food & Dining
- **PayTM** → Food & Dining
- **APSRTC** → Transportation
- **HCL Technologies** → Salary
- **NEFT CR** → Transfer In (if positive) or Salary (if from company)

You can add more keywords to the categorization logic if needed.

---

## ✅ Success Criteria

After uploading, you should see:
- ✅ 49 transactions in preview
- ✅ 7 debits (negative amounts): -80, -40, -10, -25, -30, -185, -315
- ✅ 1 credit (positive amount): +29500
- ✅ Dates in December 2025
- ✅ Categories assigned automatically
- ✅ Payment methods detected (UPI, Netbanking)

**Net Balance Check**: 29500 - (80 + 40 + 10 + 25 + 30 + 185 + 315) = **28,815** ✓

---

## 📞 Still Having Issues?

Check the browser console for error messages and share:
1. The exact column names shown in `[Excel Parse] First row columns:`
2. The first row data shown in `[Excel Parse] First row data:`
3. Any error messages in red
4. How many transactions were actually parsed

This will help identify the exact issue!
