import pandas as pd
from sqlalchemy import create_engine, text
import random
from datetime import datetime, timedelta
import json

# CONNECT TO DATABASE
# UPDATED: Pointing to 'ai_hackathon_test'
db_str = 'postgresql://neondb_owner:npg_aj5kWuP9LoCe@ep-calm-thunder-a1tgpch5-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
engine = create_engine(db_str)


def generate_fake_data():
    # ==========================================
    # STEP 0: CLEANUP
    # ==========================================
    print("⚠️ Forcing clean schema reset...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS production_logs CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS suppliers CASCADE;"))
        conn.commit()
    print("✅ Tables dropped.")

    # ==========================================
    # STEP 0B: SCHEMA RECREATION (UPDATED)
    # ==========================================
    print("🔨 Recreating database schema...")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE suppliers (
                supplier_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location TEXT NOT NULL,
                eligibility JSONB,
                description JSONB,
                reliability_score INT DEFAULT 0
            );
        """))
        conn.execute(text("""
            CREATE TABLE transactions (
                transaction_id VARCHAR(50) PRIMARY KEY,
                supplier_id VARCHAR(50) NOT NULL,
                amount INT NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
                date TIMESTAMP NOT NULL DEFAULT NOW(),
                quality JSONB,
                status VARCHAR(50) NOT NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
            );
        """))
        conn.execute(text("""
            CREATE TABLE production_logs (
                log_id VARCHAR(50) PRIMARY KEY,
                date TIMESTAMP NOT NULL DEFAULT NOW(),
                product_type VARCHAR(100) NOT NULL,
                quantity INT NOT NULL,
                supplier_id VARCHAR(50) NOT NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
            );
        """))
        conn.commit()
    print("✅ Schema recreated successfully.")

    # ==========================================
    # PART 1: CREATE SUPPLIERS (UPDATED FIELDS)
    # ==========================================
    suppliers = [
        {
            "supplier_id": "SUP-DVO-001",
            "name": "Davao Golden Cacao Coop",
            "location": "Davao City, Calinan, Wangan",
            "eligibility": json.dumps({"philgap_certified": True, "philgap_id": "BPI-2023-11"}),
            "description": json.dumps({
                "bearing_trees": 2000,
                "total_hectares": 5.0,
                "elevation_meters": 450,
                "soil_type": "loamy",
                "annual_rainfall_mm": 1800
            }),
            "reliability_score": 85
        },
        {
            "supplier_id": "SUP-DVO-099",
            "name": "Baguio District Aggregators",
            "location": "Davao City, Baguio, Tawan-Tawan",
            "eligibility": json.dumps({"philgap_certified": False}),
            "description": json.dumps({
                "bearing_trees": 500,
                "total_hectares": 2.0,
                "elevation_meters": 450,
                "soil_type": "loamy",
                "annual_rainfall_mm": 1800
            }),
            "reliability_score": 65
        }
    ]

    print("1. Inserting Suppliers...")
    with engine.connect() as conn:
        for s in suppliers:
            query = text("""
                INSERT INTO suppliers (supplier_id, name, location, eligibility, description, reliability_score)
                VALUES (:supplier_id, :name, :location, :eligibility, :description, :reliability_score)
                ON CONFLICT (supplier_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    location = EXCLUDED.location,
                    eligibility = EXCLUDED.eligibility,
                    description = EXCLUDED.description,
                    reliability_score = EXCLUDED.reliability_score;
            """)
            conn.execute(query, s)
            conn.commit()
    print("✅ Suppliers added/updated.")

    # ==========================================
    # PART 2: CREATE TRANSACTIONS (UPDATED FIELDS)
    # ==========================================
    transactions = []
    start_date = datetime.now() - timedelta(days=180)
    current_delivery_date = start_date
    txn_count = 0
    supplier_ids = ['SUP-DVO-001', 'SUP-DVO-099']

    while current_delivery_date < datetime.now():
        amount = random.randint(100, 110)
        if current_delivery_date.month in [10, 11, 12]:
            amount = int(amount * 1.20)

        is_good = random.choice([True, True, True, False])
        if is_good:
            quality = {"moisture_content": round(random.uniform(6.0, 7.5), 1),
                       "cut_test_results": {"moldy_percent": 1.0, "insect_damaged_percent": 0.5}}
            price = 125.00
            status = "completed"
        else:
            quality = {"moisture_content": round(random.uniform(8.0, 12.0), 1),
                       "cut_test_results": {"moldy_percent": 6.0, "insect_damaged_percent": 2.0}}
            price = 60.00
            status = "rejected" if random.random() < 0.3 else "completed"

        transactions.append({
            "transaction_id": f"TXN-FIXED-{txn_count}",
            "supplier_id": supplier_ids[txn_count % len(supplier_ids)],
            "date": current_delivery_date,
            "amount": amount,
            "price": price,
            "quality": json.dumps(quality),
            "status": status
        })

        current_delivery_date += timedelta(days=14)
        txn_count += 1

    print(f"2. Inserting {txn_count} transactions...")
    with engine.connect() as conn:
        for t in transactions:
            query = text("""
                INSERT INTO transactions (transaction_id, supplier_id, date, amount, price, quality, status)
                VALUES (:transaction_id, :supplier_id, :date, :amount, :price, :quality, :status)
                ON CONFLICT (transaction_id) DO NOTHING
            """)
            conn.execute(query, t)
            conn.commit()
    print(f"✅ Successfully added {txn_count} transactions!")

    # ==========================================
    # PART 3: CREATE PRODUCTION LOGS (UPDATED FIELDS)
    # ==========================================
    production_logs = []
    current_sim_date = start_date
    log_count = 0

    while current_sim_date < datetime.now():
        quantity = random.randint(75, 95)
        if current_sim_date.month in [2, 12]:
            quantity += random.randint(40, 60)

        production_logs.append({
            "log_id": f"LOG-{log_count}",
            "date": current_sim_date,
            "product_type": "Dark Chocolate",
            "quantity": quantity,
            "supplier_id": supplier_ids[log_count % len(supplier_ids)]
        })

        current_sim_date += timedelta(days=1)
        log_count += 1

    print(f"3. Inserting {log_count} production logs...")
    with engine.connect() as conn:
        for log in production_logs:
            query = text("""
                INSERT INTO production_logs (log_id, date, product_type, quantity, supplier_id)
                VALUES (:log_id, :date, :product_type, :quantity, :supplier_id)
                ON CONFLICT (log_id) DO NOTHING
            """)
            conn.execute(query, log)
            conn.commit()

    print(f"✅ Successfully added {log_count} production logs.")
    engine.dispose()
    print("✅ Database connection disposed, ready for fresh AI run.")

if __name__ == "__main__":
    generate_fake_data()