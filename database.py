import sqlite3

def medication_exists(medication_name):
    """
    Check if a medication exists in the database by name.

    Args:
        medication_name (str): Medication name in English or Hebrew

    Returns:
        dict: {
            "found": bool,
            "medication": {"id", "name_english", "name_hebrew"} or None
        }
    """
    try:
        with sqlite3.connect('pharmacy.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''
                    SELECT id, name_english, name_hebrew
                    FROM medications
                    WHERE LOWER(name_english) = LOWER(?) 
                       OR name_hebrew = ?
                ''', (medication_name, medication_name))

            result = cursor.fetchone()

            if result:
                return {
                    "found": True,
                    "medication": {
                        "id": result[0],
                        "name_english": result[1],
                        "name_hebrew": result[2],
                    }
                }
            else:
                return {
                    "found": False,
                    "medication": None
                }

    except sqlite3.Error as e:
        return {
            "found": False,
            "medication": None,
            "error": f"Database error: {str(e)}"
        }


def get_medication_availability(medication_id):
    """
    Get the availability and price of a medication (commercial information).

    This function retrieves stock status and pricing information for a specific
    medication. Use this AFTER calling medication_exists() to get the medication ID.

    Args:
        medication_id (int): The unique database ID of the medication

    Returns:
        dict: A dictionary containing:
            - "found" (bool): True if medication exists, False otherwise
            - "in_stock" (bool): True if available, False if out of stock
            - "stock_quantity" (int): Current quantity in stock
            - "price" (float): Price in Israeli Shekels (₪)
            - "error" (str, optional): Error message if database error occurred
    """
    try:
        with sqlite3.connect('pharmacy.db') as conn:
            cursor = conn.cursor()

            # Query only stock and price (minimal data)
            cursor.execute('''
                SELECT stock_quantity, price
                FROM medications
                WHERE id = ?
            ''', (medication_id,))

            result = cursor.fetchone()

            # Medication not found
            if not result:
                return {"found": False}

            # Return availability information
            return {
                "found": True,
                "in_stock": result[0] > 0,
                "stock_quantity": result[0],
                "price": result[1]
            }

    except sqlite3.Error as e:
        # Handle database errors gracefully
        return {
            "found": False,
            "error": f"Database error: {str(e)}"
        }

def get_medication_profile(medication_id, id_number=None):
    """
    Get the medical/factual profile of a medication from its leaflet.
    This includes dosage, usage instructions, factual info, and active ingredients.

    If the medication requires a prescription and id_number is provided,
    checks if the user has a valid prescription before returning sensitive information.

    Args:
        medication_id (int): Medication ID from database
        id_number (str, optional): User's ID number for prescription check

    Returns:
        dict: {
            "found": bool,
            "requires_prescription": bool,
            "has_prescription": bool (if id_number provided),
            "can_access": bool,
            "active_ingredients": str (if accessible),
            "dosage_instructions": str (if accessible),
            "usage_instructions": str (if accessible),
            "factual_info": str (if accessible),
            "message": str (if access denied),
            "error": str (if database error)
        }
    """
    try:
        with sqlite3.connect('pharmacy.db') as conn:
            cursor = conn.cursor()

            # Query profile information
            cursor.execute('''
                SELECT active_ingredients, dosage_instructions, usage_instructions,
                       factual_info, requires_prescription
                FROM medications
                WHERE id = ?
            ''', (medication_id,))

            result = cursor.fetchone()

            if not result:
                return {
                    "found": False,
                    "can_access": False
                }

            requires_prescription = bool(result[4])

            # Check prescription requirement
            if requires_prescription and id_number:
                prescription_check = check_user_prescription(id_number, medication_id)
                has_prescription = prescription_check["has_prescription"]

                if not has_prescription:
                    return {
                        "found": True,
                        "requires_prescription": True,
                        "has_prescription": False,
                        "can_access": False,
                        "message": "This medication requires a prescription. You don't have an active prescription for this medication. Please consult your doctor."
                    }

            # Return full information
            return {
                "found": True,
                "requires_prescription": requires_prescription,
                "has_prescription": True if (requires_prescription and id_number) else None,
                "can_access": True,
                "active_ingredients": result[0],
                "dosage_instructions": result[1],
                "usage_instructions": result[2],
                "factual_info": result[3]
            }

    except sqlite3.Error as e:
        return {
            "found": False,
            "can_access": False,
            "error": f"Database error: {str(e)}"
        }

def verify_user(id_number):
    """
    Verify a user exists in the system by their ID number.

    Args:
        id_number (str): User's ID number (Israeli ID)

    Returns:
        dict: {
            "verified": bool,
            "user": {
                "id_number": str,
                "first_name": str,
                "last_name": str
            } or None,
            "error": str (optional, if database error)
        }
    """
    try:
        with sqlite3.connect('pharmacy.db') as conn:
            cursor = conn.cursor()

            # Search by ID number (PRIMARY KEY)
            cursor.execute('''
                SELECT id_number, first_name, last_name
                FROM users
                WHERE id_number = ?
            ''', (id_number,))

            result = cursor.fetchone()

            if not result:
                return {
                    "verified": False,
                    "user": None
                }

            return {
                "verified": True,
                "user": {
                    "id_number": result[0],
                    "first_name": result[1],
                    "last_name": result[2]
                }
            }

    except sqlite3.Error as e:
        return {
            "verified": False,
            "user": None,
            "error": f"Database error: {str(e)}"
        }

def check_user_prescription(id_number, medication_id):
    """
    Check if a user has a prescription for a specific medication.

    Args:
        id_number (str): User's ID number
        medication_id (int): Medication ID

    Returns:
        dict: {
            "has_prescription": bool,
            "error": str (optional, if database error)
        }
    """
    try:
        with sqlite3.connect('pharmacy.db') as conn:
            cursor = conn.cursor()

            # Check if prescription exists (optimized with LIMIT 1)
            cursor.execute('''
                SELECT 1
                FROM prescriptions
                WHERE id_number = ? AND medication_id = ?
                LIMIT 1
            ''', (id_number, medication_id))

            result = cursor.fetchone()

            return {
                "has_prescription": result is not None
            }

    except sqlite3.Error as e:
        return {
            "has_prescription": False,
            "error": f"Database error: {str(e)}"
        }

