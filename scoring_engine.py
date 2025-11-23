import pandas as pd
from sqlalchemy import create_engine, text
import json
from datetime import datetime

# 1. CONNECT TO DATABASE
# Ask your friend for the 'postgres' password
db_str = 'postgresql://neondb_owner:npg_VhvNzRaM3xi8@ep-young-fire-a1mrxhwn-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
engine = create_engine(db_str)


def calculate_scores():
    try:
        # ---------------------------------------------------------
        # STEP 1: GET THE DATA
        # ---------------------------------------------------------
        query = """
        SELECT 
            t.supplier_id,
            t.date,
            t.amount,
            t.quality,
            s.reliability_score,       
            s.description,        
            s.eligibility    
        FROM transactions t 
        JOIN suppliers s ON t.supplier_id = s.supplier_id
        """
        df = pd.read_sql(query, engine)

        if df.empty:
            print("⚠️ No matching data found. Did you run the Seeder?")
            return

        # ---------------------------------------------------------
        # STEP 2: CALCULATE THE 4 FACTORS
        # ---------------------------------------------------------
        supplier_scores = []

        for supplier_id, group in df.groupby('supplier_id'):

            # A. SEASONALITY
            last_delivery = pd.to_datetime(group['date'].max())
            days_since = (datetime.now() - last_delivery).days
            seasonality_score = max(0, 100 - (days_since * 2))

            # B. VOLUME
            farm_data = group['description'].iloc[0]
            if isinstance(farm_data, str): farm_data = json.loads(farm_data)
            bearing_trees = farm_data.get('bearing_trees', 100)

            total_delivered = group['amount'].sum()
            expected_yield = bearing_trees * 2.0
            if expected_yield == 0: expected_yield = 1

            volume_score = min(100, (total_delivered / expected_yield) * 100)

            # C. QUALITY
            quality_scores = []
            for audit in group['quality']:
                if isinstance(audit, str): audit = json.loads(audit)
                q_score = 100
                cut_test = audit.get('cut_test_results', {})

                if cut_test.get('moldy_percent', 0) > 3.0: q_score -= 40
                if cut_test.get('insect_damaged_percent', 0) > 2.5: q_score -= 20
                if audit.get('moisture_content', 7.0) > 8.0: q_score -= 20
                quality_scores.append(max(0, q_score))

            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0

            # D. PHILGAP
            compliance = group['eligibility'].iloc[0]
            if isinstance(compliance, str): compliance = json.loads(compliance)
            philgap_score = 100 if compliance.get('philgap_certified') else 0

            # FORMULA
            final_score = (
                    (seasonality_score * 0.40) +
                    (volume_score * 0.30) +
                    (avg_quality_score * 0.20) +
                    (philgap_score * 0.10)
            )

            supplier_scores.append({
                "supplier_id": supplier_id,
                "score": int(final_score)
            })

        # ---------------------------------------------------------
        # STEP 3: UPDATE THE DATABASE (The "Safe" Block)
        # ---------------------------------------------------------
        print(f"--- UPDATING SCORES for {len(supplier_scores)} Suppliers ---")

        # engine.begin() AUTOMATICALLY commits or rolls back if error
        with engine.begin() as conn:
            for item in supplier_scores:
                update_query = text("""
                    UPDATE suppliers 
                    SET reliability_score = :score 
                    WHERE supplier_id = :id
                """)
                conn.execute(update_query, {"score": item['score'], "id": item['supplier_id']})

        print("✅ Database update successful.")

    except Exception as e:
        print(f"❌ Critical Error in Scoring Engine: {e}")


if __name__ == "__main__":
    calculate_scores()