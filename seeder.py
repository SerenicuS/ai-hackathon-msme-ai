import pandas as pd
from sqlalchemy import create_engine, text
import random
from datetime import datetime, timedelta
import json

# CONNECT TO DATABASE
db_str = 'postgresql://neondb_owner:npg_VhvNzRaM3xi8@ep-young-fire-a1mrxhwn-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
engine = create_engine(db_str)


def generate_fake_data():
    # ==========================================
    # 💥 PART 0: CLEAN UP OLD TRANSACTIONAL DATA
    # ==========================================
    print("0. Cleaning old transactional data (starting fresh)...")
    with engine.begin() as conn:
        # We use TRUNCATE for speed and cleanliness. CASCADE handles foreign keys if any.
        conn.execute(text("TRUNCATE TABLE transactions CASCADE;"))
        conn.execute(text("TRUNCATE TABLE production_logs CASCADE;"))
    print("✅ Old transactions and logs deleted.")

    # ==========================================
    # PART 1: CREATE SUPPLIERS
    # ==========================================
    suppliers = [
        {
            "supplier_id": "SUP-DVO-001",
            "name": "Davao Golden Cacao Coop",
            "location": "{\"city\": \"Davao City\", \"district\": \"Calinan\", \"area\": \"Wangan\"}",
            "eligibility": "{\"philgap_certified\": true, \"philgap_id\": \"BPI-2023-11\"}",
            "description": "{\"bearing_trees\": 2000, \"total_hectares\": 5.0, \"elevation_meters\": 450, \"soil_type\": \"loamy\", \"annual_rainfall_mm\": 1800}",
            "reliability_score": 85
        },
        {
            "supplier_id": "SUP-DVO-099",
            "name": "Baguio District Aggregators",
            "location": "{\"city\": \"Davao City\", \"district\": \"Baguio\", \"area\": \"Tawan-Tawan\"}",
            "eligibility": "{\"philgap_certified\": false}",
            "description": "{\"bearing_trees\": 500, \"total_hectares\": 2.0, \"elevation_meters\": 450, \"soil_type\": \"loamy\", \"annual_rainfall_mm\": 1800}",
            "reliability_score": 65
        },
        {
            "supplier_id": "SUP-DVO-002",
            "name": "Malagos Valley Growers",
            "location": "{\"city\": \"Davao City\", \"district\": \"Baguio\", \"area\": \"Malagos\"}",
            "eligibility": "{\"philgap_certified\": true, \"philgap_id\": \"BPI-2024-01\"}",
            "description": "{\"bearing_trees\": 5000, \"total_hectares\": 8.0, \"elevation_meters\": 350, \"soil_type\": \"volcanic loam\", \"annual_rainfall_mm\": 2100}",
            "reliability_score": 92
        },
        {
            "supplier_id": "SUP-DVO-003",
            "name": "Paquibato Highland Farms",
            "location": "{\"city\": \"Davao City\", \"district\": \"Paquibato\", \"area\": \"Malabog\"}",
            "eligibility": "{\"philgap_certified\": false}",
            "description": "{\"bearing_trees\": 800, \"total_hectares\": 1.5, \"elevation_meters\": 700, \"soil_type\": \"clay-loam\", \"annual_rainfall_mm\": 1750}",
            "reliability_score": 70
        },
        {
            "supplier_id": "SUP-DVO-004",
            "name": "Tugbok Cacao Alliance",
            "location": "{\"city\": \"Davao City\", \"district\": \"Tugbok\", \"area\": \"Mintal\"}",
            "eligibility": "{\"philgap_certified\": true, \"philgap_id\": \"BPI-2023-05\"}",
            "description": "{\"bearing_trees\": 3500, \"total_hectares\": 6.0, \"elevation_meters\": 200, \"soil_type\": \"sandy loam\", \"annual_rainfall_mm\": 1900}",
            "reliability_score": 88
        },
        {
            "supplier_id": "SUP-DVO-005",
            "name": "Toril Eco-Agri Ventures",
            "location": "{\"city\": \"Davao City\", \"district\": \"Toril\", \"area\": \"Eden\"}",
            "eligibility": "{\"philgap_certified\": false}",
            "description": "{\"bearing_trees\": 1200, \"total_hectares\": 3.0, \"elevation_meters\": 800, \"soil_type\": \"volcanic\", \"annual_rainfall_mm\": 2200}",
            "reliability_score": 78
        },
        {
            "supplier_id": "SUP-DVO-006",
            "name": "Marilog Indigenous Farmers",
            "location": "{\"city\": \"Davao City\", \"district\": \"Marilog\", \"area\": \"Baganihan\"}",
            "eligibility": "{\"philgap_certified\": true, \"philgap_id\": \"BPI-2024-03\"}",
            "description": "{\"bearing_trees\": 600, \"total_hectares\": 2.0, \"elevation_meters\": 1100, \"soil_type\": \"limestone rich\", \"annual_rainfall_mm\": 1650}",
            "reliability_score": 75
        },
        {
            "supplier_id": "SUP-DVO-007",
            "name": "Tigatto Riverbank Cacao",
            "location": "{\"city\": \"Davao City\", \"district\": \"Buhangin\", \"area\": \"Tigatto\"}",
            "eligibility": "{\"philgap_certified\": true, \"philgap_id\": \"BPI-2023-12\"}",
            "description": "{\"bearing_trees\": 1500, \"total_hectares\": 2.5, \"elevation_meters\": 100, \"soil_type\": \"alluvial\", \"annual_rainfall_mm\": 1850}",
            "reliability_score": 82
        },
        {
            "supplier_id": "SUP-DVO-008",
            "name": "Subasta Integrated Farms",
            "location": "{\"city\": \"Davao City\", \"district\": \"Calinan\", \"area\": \"Subasta\"}",
            "eligibility": "{\"philgap_certified\": true, \"philgap_id\": \"BPI-2022-09\"}",
            "description": "{\"bearing_trees\": 4000, \"total_hectares\": 7.5, \"elevation_meters\": 400, \"soil_type\": \"loamy\", \"annual_rainfall_mm\": 2000}",
            "reliability_score": 90
        },
        {
            "supplier_id": "SUP-DVO-009",
            "name": "Matina Small Holders",
            "location": "{\"city\": \"Davao City\", \"district\": \"Talomo\", \"area\": \"Matina Pangi\"}",
            "eligibility": "{\"philgap_certified\": false}",
            "description": "{\"bearing_trees\": 300, \"total_hectares\": 1.0, \"elevation_meters\": 50, \"soil_type\": \"silt loam\", \"annual_rainfall_mm\": 1950}",
            "reliability_score": 60
        },
        {
            "supplier_id": "SUP-DVO-010",
            "name": "Mount Apo Foothill Coop",
            "location": "{\"city\": \"Davao City\", \"district\": \"Calinan\", \"area\": \"Cawayan\"}",
            "eligibility": "{\"philgap_certified\": true, \"philgap_id\": \"BPI-2024-05\"}",
            "description": "{\"bearing_trees\": 10000, \"total_hectares\": 20.0, \"elevation_meters\": 550, \"soil_type\": \"volcanic loam\", \"annual_rainfall_mm\": 2300}",
            "reliability_score": 95
        },
        {
            "supplier_id": "SUP-DVO-011",
            "name": "Acacia Farm Agri-Ventures",
            "location": "{\"city\": \"Davao City\", \"district\": \"Sasa\", \"area\": \"Panacan\"}",
            "eligibility": "{\"philgap_certified\": false}",
            "description": "{\"bearing_trees\": 1800, \"total_hectares\": 4.0, \"elevation_meters\": 80, \"soil_type\": \"clay-rich\", \"annual_rainfall_mm\": 1700}",
            "reliability_score": 72
        }
    ]

    print("1. Inserting Suppliers...")
    with engine.begin() as conn:
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
    print("✅ Suppliers added/updated.")

    # ==========================================
    # PART 2: TRANSACTIONS (The "Slow Burn" Strategy)
    # ==========================================
    transactions = []
    supplier_ids = [s['supplier_id'] for s in suppliers]
    start_date = datetime.now() - timedelta(days=120)  # 4 months history

    # 1. THE BIG STARTER PACK
    # We need a huge starting amount because we are going to burn through it fast.
    transactions.append({
        "transaction_id": "TXN-START-000",
        "supplier_id": supplier_ids[0],
        "date": start_date,
        "amount": 4500,  # <--- INCREASED TO 4,500kg
        "price": 120.00,
        "quality": json.dumps({"moisture": 7.0}),
        "status": "completed"
    })

    current_delivery_date = start_date + timedelta(days=5)
    txn_count = 1

    while current_delivery_date < datetime.now():
        # FIX: Buy LESS (350-450kg)
        amount = random.randint(350, 450)

        transactions.append({
            "transaction_id": f"TXN-AUTO-{txn_count}",
            "supplier_id": supplier_ids[txn_count % len(supplier_ids)],
            "date": current_delivery_date,
            "amount": amount,
            "price": 125.00,
            "quality": json.dumps({"moisture": 7.2}),
            "status": "completed"
        })

        # Frequency: Every 10 days
        current_delivery_date += timedelta(days=10)
        txn_count += 1

    print(f"2. Inserting {len(transactions)} transactions...")
    with engine.begin() as conn:
        for t in transactions:
            conn.execute(text("""
                    INSERT INTO transactions (transaction_id, supplier_id, date, amount, price, quality, status)
                    VALUES (:transaction_id, :supplier_id, :date, :amount, :price, :quality, :status)
                    ON CONFLICT DO NOTHING
                """), t)

    # ==========================================
    # PART 3: PRODUCTION (High Consumption)
    # ==========================================
    production_logs = []
    current_sim_date = start_date
    log_count = 0

    while current_sim_date < datetime.now():
        # FIX: Cook CONSISTENTLY (140-160kg)
        # 150kg * 13 batches/mo = ~1,950kg Outflow
        # vs Inflow of ~1,200kg (400*3)
        # Net Loss: ~750kg per month. Perfect trend downwards.
        quantity = random.randint(140, 160)

        # Cook on Mon, Wed, Fri
        if current_sim_date.weekday() in [0, 2, 4]:
            production_logs.append({
                "log_id": f"LOG-DEMO-{log_count}",
                "date": current_sim_date,
                "product_type": "Dark Chocolate",
                "quantity": quantity,
                "supplier_id": supplier_ids[log_count % len(supplier_ids)]
            })
            log_count += 1
        current_sim_date += timedelta(days=1)

    print(f"3. Inserting {len(production_logs)} logs...")
    with engine.begin() as conn:
        for log in production_logs:
            conn.execute(text("""
                    INSERT INTO production_logs (log_id, date, product_type, quantity, supplier_id)
                    VALUES (:log_id, :date, :product_type, :quantity, :supplier_id)
                    ON CONFLICT DO NOTHING
                """), log)

    print("✅ DONE. Data is tuned for a 'Critical' downward trend.")

if __name__ == "__main__":
    # Optional: wipe old data before generating new
    # with engine.connect() as conn:
    #     conn.execute(text("DELETE FROM transactions; DELETE FROM production_logs;"))
    #     conn.commit()

    generate_fake_data()