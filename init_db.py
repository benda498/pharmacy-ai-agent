import sqlite3

def init_database():
    """Creates the database and tables with initial data"""

    # Connect to database
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()

    # Drop existing tables (fresh start)
    cursor.execute('DROP TABLE IF EXISTS medications')
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS prescriptions')

    # Create medications table
    cursor.execute('''
        CREATE TABLE medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_english TEXT NOT NULL UNIQUE,
            name_hebrew TEXT NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            price REAL DEFAULT 0.0,
            dosage_instructions TEXT,
            usage_instructions TEXT,
            requires_prescription INTEGER DEFAULT 0,
            factual_info TEXT,
            active_ingredients TEXT
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id_number TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT
        )
    ''')

    # Create prescriptions table
    cursor.execute('''
            CREATE TABLE prescriptions (
                id_number TEXT NOT NULL,
                medication_id INTEGER NOT NULL,
                PRIMARY KEY (id_number, medication_id),
                FOREIGN KEY (id_number) REFERENCES users(id_number),
                FOREIGN KEY (medication_id) REFERENCES medications(id)
            )
        ''')

    # Insert 5 medications
    medications = [
        ('Acamol', 'אקמול', 150, 25.90,
         'Adults: 1-2 tablets every 6-8 hours. Max 8 tablets per day.',
         'Take with water. Can be taken with or without food.',
         0,  # No prescription required
         'Pain reliever and fever reducer. Effective for headaches, muscle pain, and fever.',
         'Paracetamol 500mg'),

        ('Optalgin', 'אופטלגין', 0, 32.50,
         'Adults: 1 tablet up to 3 times daily.',
         'Take with food to reduce stomach irritation.',
         0,  # No prescription required
         'Pain reliever for moderate to severe pain. Effective for headaches and menstrual pain.',
         'Metamizole 500mg'),

        ('Augmentin', 'אוגמנטין', 45, 89.00,
         'Adults: 1 tablet twice daily for 7-10 days.',
         'Complete the full course even if symptoms improve. Take with food.',
         1,  # Prescription required
         'Antibiotic for bacterial infections. Used for respiratory, urinary, and skin infections.',
         'Amoxicillin 875mg + Clavulanic acid 125mg'),

        ('Advil', 'אדוויל', 200, 28.90,
         'Adults: 1-2 tablets every 6-8 hours. Max 6 tablets per day.',
         'Take with food or milk to reduce stomach upset.',
         0,  # No prescription required
         'Anti-inflammatory pain reliever. Effective for pain, inflammation, and fever.',
         'Ibuprofen 400mg'),

        ('Nurofen', 'נורופן', 80, 35.00,
         'Adults: 1 tablet every 6-8 hours as needed. Max 3 tablets per day.',
         'Take with food or milk. Do not exceed recommended dose.',
         0,  # No prescription required
         'Fast-acting pain and inflammation relief. Suitable for headaches, dental pain, and fever.',
         'Ibuprofen 400mg')
    ]

    cursor.executemany('''
        INSERT INTO medications 
        (name_english, name_hebrew, stock_quantity, price, 
         dosage_instructions, usage_instructions, requires_prescription, 
         factual_info, active_ingredients)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', medications)

    # Insert 10 users
    users = [
        ('123456789', 'David', 'Cohen', '050-1234567'),
        ('234567890', 'Sarah', 'Levi', '052-9876543'),
        ('345678901', 'Michael', 'Mizrahi', '053-5551234'),
        ('456789012', 'Rachel', 'Katz', '054-7778888'),
        ('567890123', 'Yossi', 'Avraham', '050-3334444'),
        ('678901234', 'Leah', 'Friedman', '052-6665555'),
        ('789012345', 'Avi', 'Shapiro', '053-9990000'),
        ('890123456', 'Tamar', 'Ben-David', '054-1112222'),
        ('901234567', 'Eli', 'Goldstein', '050-4445555'),
        ('012345678', 'Miriam', 'Rosenberg', '052-8889999')
    ]

    cursor.executemany('''
        INSERT INTO users 
        (id_number, first_name, last_name, phone)
        VALUES (?, ?, ?, ?)
    ''', users)

    # Insert prescriptions (link users to prescription medications)
    prescriptions = [
        # David Cohen has prescription for Augmentin
        ('123456789', 3),

        # Yossi Avraham has prescription for Augmentin
        ('567890123', 3),

        # Rachel Katz has prescription for Augmentin
        ('456789012', 3),
    ]

    cursor.executemany('''
            INSERT INTO prescriptions 
            (id_number, medication_id)
            VALUES (?, ?)
        ''', prescriptions)

    # Save and close
    conn.commit()
    conn.close()

    print("Database initialized successfully!")
    print(f"   - Created 'pharmacy.db'")
    print(f"   - Added {len(medications)} medications")
    print(f"   - Added {len(users)} users")

if __name__ == "__main__":
    init_database()
