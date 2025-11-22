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
    # STEP 0: CLEANUP (THE FIX FOR BLOAT)
    # ==========================================

    print("⚠️ Forcing clean schema reset...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS production_logs;"))
        conn.execute(text("DROP TABLE IF EXISTS transactions;"))
        conn.execute(text("DROP TABLE IF EXISTS supplier_profiles CASCADE;"))
        conn.commit()
    print("✅ Tables dropped.")
    print("🌱 Planting fake Cacao data...")

    # ==========================================
    # STEP 0B: SCHEMA RECREATION (CREATE) <--- THIS IS THE MISSING PIECE
    # ==========================================
    print("🔨 Recreating database schema...")
    with engine.connect() as conn:
        conn.execute(text("""
                CREATE TABLE supplier_profiles (
                    supplier_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    location JSONB,
                    compliance_status JSONB,
                    farm_profile JSONB,
                    ai_reliability_score INT DEFAULT 0
                );
            """))
        # IN seeder.py, inside the STEP 0B: SCHEMA RECREATION (CREATE) block
        conn.execute(text("""
                    CREATE TABLE transactions (
                        transaction_id VARCHAR(50) PRIMARY KEY,
                        supplier_id VARCHAR(50) REFERENCES supplier_profiles(supplier_id) ON DELETE CASCADE,
                        date TIMESTAMP NOT NULL,
                        price_per_kg NUMERIC(10, 2), -- Use high precision numeric for money
                        net_weight_kg NUMERIC(15, 2), -- Use high precision numeric for inventory weight
                        quality_audit JSONB
                    );
                """))
        conn.execute(text("""
                    CREATE TABLE production_logs (
                        log_id SERIAL PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        kilos_processed NUMERIC(15, 2) NOT NULL, -- Ensure consumption is also high precision
                        product_type TEXT DEFAULT 'Tablea'
                    );
                """))
        conn.commit()
    print("✅ Schema recreated successfully.")

    # ==========================================
    # PART 1: CREATE SUPPLIERS (Associations)
    # ==========================================
    suppliers = [
        {
            "supplier_id": "SUP-DVO-001",
            "name": "Davao Golden Cacao Coop",
            "location": json.dumps({
                "region": "Region XI",
                "city": "Davao City",
                "district": "Calinan",
                "barangay": "Wangan"
            }),
            "compliance": json.dumps({"philgap_certified": True, "philgap_id": "BPI-2023-11"}),
            "profile": json.dumps({
                "bearing_trees": 2000,
                "total_hectares": 5.0,
                "elevation_meters": 450,
                "soil_type": "loamy",
                "annual_rainfall_mm": 1800
            })
        },
        {
            "supplier_id": "SUP-DVO-099",
            "name": "Baguio District Aggregators",
            "location": json.dumps({
                "region": "Region XI",
                "city": "Davao City",
                "district": "Baguio",
                "barangay": "Tawan-Tawan"
            }),
            "compliance": json.dumps({"philgap_certified": False}),
            "profile": json.dumps({
                "bearing_trees": 500,
                "total_hectares": 2.0,
                "elevation_meters": 450,
                "soil_type": "loamy",
                "annual_rainfall_mm": 1800
            })
        }
    ]

    print("1. Inserting Supplier Associations...")
    with engine.connect() as conn:
        for s in suppliers:
            query = text("""
                    INSERT INTO supplier_profiles (supplier_id, name, location, compliance_status, farm_profile)
                    VALUES (:supplier_id, :name, :location, :compliance, :profile)
                    ON CONFLICT (supplier_id) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        location = EXCLUDED.location,
                        farm_profile = EXCLUDED.farm_profile;
                """)
            conn.execute(query, s)
            conn.commit()
    print("✅ Associations added/updated.")

    # ==========================================
    # PART 2: CREATE TRANSACTIONS (Supply In) - FIXED BI-WEEKLY SCHEDULE
    # ==========================================
    transactions = []
    start_date = datetime.now() - timedelta(days=180)
    current_delivery_date = start_date
    txn_count = 0

    # Cycle through suppliers to alternate deliveries
    supplier_ids = ['SUP-DVO-001', 'SUP-DVO-099']

    # Loop to create transactions every 14 days for the 180-day history
    while current_delivery_date < datetime.now():

        # Base delivery volume set high (approx 1,250 kg) to meet 2.5 ton/month demand
        base_weight = random.randint(100, 110)

        # Simulate Seasonality
        # Apply proportional spike during peak harvest
        if current_delivery_date.month in [10, 11, 12]:
            base_weight = int(base_weight * 1.20)  # 20% increase during peak harvest (e.g., 1500 kg max)

        # Simulate Quality (simplified) - Keep your existing quality logic
        is_good = random.choice([True, True, True, False])
        if is_good:
            quality = {"moisture_content": round(random.uniform(6.0, 7.5), 1),
                       "cut_test_results": {"moldy_percent": 1.0, "insect_damaged_percent": 0.5}}
            price = 125.00
        else:
            quality = {"moisture_content": round(random.uniform(8.0, 12.0), 1),
                       "cut_test_results": {"moldy_percent": 6.0, "insect_damaged_percent": 2.0}}
            price = 60.00

        transactions.append({
            "transaction_id": f"TXN-FIXED-{txn_count}",
            "supplier_id": supplier_ids[txn_count % len(supplier_ids)],  # Alternates SUP-DVO-001 and SUP-DVO-099
            "date": current_delivery_date,
            "price_per_kg": price,
            "net_weight_kg": base_weight,
            "quality_audit": json.dumps(quality)
        })

        # Move to the next delivery date
        current_delivery_date += timedelta(days=14)
        txn_count += 1

    print(f"2. Inserting {txn_count} bi-weekly transactions...")
    with engine.connect() as conn:
        for t in transactions:
            query = text("""
                    INSERT INTO transactions (transaction_id, supplier_id, date, price_per_kg, net_weight_kg, quality_audit)
                    VALUES (:transaction_id, :supplier_id, :date, :price_per_kg, :net_weight_kg, :quality_audit)
                    ON CONFLICT (transaction_id) DO NOTHING
                """)
            conn.execute(query, t)
            conn.commit()
    print(f"✅ Successfully added {txn_count} historical transactions on a fixed schedule!")

    # ==========================================
    # PART 3: CREATE PRODUCTION LOGS (Demand Out) - SYNCHRONIZED
    # ==========================================
    consumption_data = []
    start_date = datetime.now() - timedelta(days=180)

    print("3. Simulating Factory Usage (Outflow)...")

    # 3a. Create the table if it doesn't exist (ensures automation works)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS production_logs (
                log_id SERIAL PRIMARY KEY,
                date TIMESTAMP NOT NULL,
                kilos_processed FLOAT NOT NULL,
                product_type TEXT DEFAULT 'Tablea'
            );
        """))
        conn.commit()

    # 3b. Generate Daily Consumption Data
    current_sim_date = start_date
    while current_sim_date < datetime.now():

        # NEW SYNCHRONIZED BASE DEMAND: Target ~85kg/day (2500 kg / 30 days)
        daily_usage = random.randint(75, 95)  # Base range for 2-3 Ton/Month MSME

        # Demand Spikes: Valentine's (Feb) & Christmas (Dec)
        if current_sim_date.month in [2, 12]:
            daily_usage += random.randint(40, 60)  # Larger holiday usage spike!

        consumption_data.append({
            "date": current_sim_date,
            "kilos_processed": daily_usage,
            "product_type": "Dark Chocolate"
        })

        current_sim_date += timedelta(days=1)

    # 3c. Insert into DB
    with engine.connect() as conn:
        for row in consumption_data:
            conn.execute(text("""
                INSERT INTO production_logs (date, kilos_processed, product_type)
                VALUES (:date, :kilos_processed, :product_type)
            """), row)
        conn.commit()

    print(f"✅ Successfully added {len(consumption_data)} days of Production Logs (Target: 2.5 Tons/Month).")
    engine.dispose()
    print("✅ Database connection disposed, ready for fresh AI run.")

if __name__ == "__main__":
    generate_fake_data()