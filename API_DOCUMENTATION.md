# API Documentation - Tools & Functions

Technical documentation for the three tools used by the pharmacy assistant agent.

---

## Tool 1: medication_exists

### 1. Name and Purpose
**Name:** `medication_exists`

**Purpose:** Search for a medication by name (English or Hebrew) and return its basic information.

### 2. Inputs
- `medication_name` (string, required) - Name of medication to search

Example: `{"medication_name": "אקמול"}`

### 3. Output Schema
```json
{
  "found": boolean,
  "medication": {
    "id": integer,
    "name_english": string,
    "name_hebrew": string
  } | null
}
```

Example (found):
```json
{
  "found": true,
  "medication": {
    "id": 1,
    "name_english": "Acamol",
    "name_hebrew": "אקמול"
  }
}
```

Example (not found):
```json
{
  "found": false,
  "medication": null
}
```

### 4. Error Handling
Uses try-except to catch `sqlite3.Error`. On database error, returns:
```json
{
  "found": false,
  "medication": null,
  "error": "Database error: [error message]"
}
```

### 5. Fallback Behavior
- Database unavailable: Returns `found: false` with error message
- Empty/invalid input: Returns `found: false, medication: null`
- No match found: Returns `found: false` (not an error)

---

## Tool 2: get_medication_availability

### 1. Name and Purpose
**Name:** `get_medication_availability`

**Purpose:** Get stock availability and price for a medication by ID.

### 2. Inputs
- `medication_id` (integer, required) - Medication ID from database

Example: `{"medication_id": 1}`

### 3. Output Schema
```json
{
  "found": boolean,
  "in_stock": boolean,
  "stock_quantity": integer,
  "price": float
}
```

Example (in stock):
```json
{
  "found": true,
  "in_stock": true,
  "stock_quantity": 150,
  "price": 25.9
}
```

Example (not found):
```json
{
  "found": false
}
```

### 4. Error Handling
Uses try-except to catch `sqlite3.Error`. On database error, returns:
```json
{
  "found": false,
  "error": "Database error: [error message]"
}
```

### 5. Fallback Behavior
- Invalid medication_id → Returns `found: false`
- Database error → Returns error response, does not crash
- Stock quantity 0 → Returns `in_stock: false`

---

## Tool 3: get_medication_profile

### 1. Name and Purpose
**Name:** `get_medication_profile`

**Purpose:** Get detailed medical information (dosage, usage, ingredients). Includes prescription validation for controlled medications.

### 2. Inputs
- `medication_id` (integer, required) - Medication ID
- `id_number` (string, optional, internal) - User ID for prescription check

Example: `{"medication_id": 3}`

### 3. Output Schema

**Success (access granted):**
```json
{
  "found": boolean,
  "requires_prescription": boolean,
  "has_prescription": boolean | null,
  "can_access": boolean,
  "active_ingredients": string,
  "dosage_instructions": string,
  "usage_instructions": string,
  "factual_info": string
}
```

**Denial (no prescription):**
```json
{
  "found": boolean,
  "requires_prescription": boolean,
  "has_prescription": boolean,
  "can_access": boolean,
  "message": string
}
```

Example (access granted):
```json
{
  "found": true,
  "requires_prescription": false,
  "can_access": true,
  "active_ingredients": "Paracetamol 500mg",
  "dosage_instructions": "Adults: 1-2 tablets every 6-8 hours.",
  "usage_instructions": "Take with water.",
  "factual_info": "Pain reliever and fever reducer."
}
```

Example (access denied):
```json
{
  "found": true,
  "requires_prescription": true,
  "has_prescription": false,
  "can_access": false,
  "message": "This medication requires a prescription. You don't have an active prescription. Please consult your doctor."
}
```

### 4. Error Handling
Uses try-except to catch `sqlite3.Error`. On database error, returns:
```json
{
  "found": false,
  "can_access": false,
  "error": "Database error: [error message]"
}
```

### 5. Fallback Behavior
- Medication not found: Returns `found: false, can_access: false`
- Prescription required but user has none: Returns `can_access: false` with message
- Database error during prescription check: Denies access (fail-safe)
- No user ID provided for prescription med: Proceeds without validation

---

## Error Handling Pattern

All functions use context managers for database connections:
```python
try:
    with sqlite3.connect('pharmacy.db') as conn:
        # Database operations
except sqlite3.Error as e:
    return {"found": False, "error": f"Database error: {str(e)}"}
```

This ensures connections are closed properly even if errors occur.

---

## Security Notes

- SQL injection prevention: All queries use parameterized statements
- Prescription validation: Checked server-side on every request
- Fail-safe: Access denied on error or missing prescription