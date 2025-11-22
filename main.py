import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine
from prophet import Prophet
import scoring_engine  # This imports the file you just made!
from sqlalchemy import text # Make sure this is imported at the top

app = FastAPI()

# Database Connection (Same as before)
db_str = 'postgresql://neondb_owner:npg_aj5kWuP9LoCe@ep-calm-thunder-a1tgpch5-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
engine = create_engine(db_str)


# =========================================================
# PART 1: THE TRIGGER (Connects Web App -> Scoring Engine)
# =========================================================
@app.post("/update-scores")
def trigger_scoring_logic():
    """
    1. RUNS the Math (updates the database).
    2. FETCHES the new Leaderboard immediately.
    3. RETURNS it to the Web App.
    """
    try:
        print("Received signal: Updating Supplier Scores...")

        # STEP 1: Run the hardcoded logic to update the DB
        scoring_engine.calculate_scores()

        # STEP 2: Immediately query the fresh data
        # We want the list sorted by Score (Highest first)
        query = """
        SELECT supplier_id, name, location, ai_reliability_score, 
               farm_profile, compliance_status
        FROM supplier_profiles 
        ORDER BY ai_reliability_score DESC
        """

        # Read into Pandas
        df = pd.read_sql(query, engine)

        # STEP 3: Convert to JSON
        # 'orient="records"' turns the table into a nice list of objects
        data_list = df.to_dict(orient="records")

        return {
            "status": "success",
            "message": "Supplier scores updated and fetched.",
            "data": data_list  # <--- THIS IS WHAT HE WANTS
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}

# =========================================================
# PART 2: THE AI (Smart Demand Forecasting)
# =========================================================
@app.get("/predict-demand")
def predict_demand():
    """
    The Web App calls this to show the "Future Demand" graph.
    This uses Facebook Prophet to analyze historical trends.
    """
    try:
        # 1. FETCH DATA: Get historical consumption (date + weight)
        # Prophet STRICTLY requires columns named 'ds' (date) and 'y' (value)
        query = """
        SELECT date as ds, net_weight_kg as y 
        FROM transactions 
        ORDER BY date
        """
        df = pd.read_sql(query, engine)

        # Safety Check: AI needs at least 2 data points to work
        if len(df) < 2:
            return {
                "status": "warning",
                "message": "Not enough data to train AI yet. Add more transactions.",
                "forecast_total": 0
            }

        # 2. TRAIN AI: Fit the model to your data
        # 'daily_seasonality=True' helps if you have data for every day
        m = Prophet(daily_seasonality=True)
        m.fit(df)

        # 3. PREDICT: Look 30 days into the future
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)

        # 4. CALCULATE: Sum of expected demand for the next 30 days
        # We take the last 30 entries of the prediction
        next_30_days = forecast.tail(30)
        total_predicted_demand = next_30_days['yhat'].sum()

        return {
            "status": "success",
            "forecast_total_kg": int(total_predicted_demand),
            "message": "Prediction complete based on historical seasonality."
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/suggest-orders-smart")
def suggest_orders_smart():
    """
    The Smartest AI Logic:
    1. Check 'Storage' (Current Stock).
    2. Predict 'Future Flow' (Inflow/Outflow).
    3. Calculate the 'True Deficit' and suggest orders from top suppliers.
    """
    try:
        # --- STEP 1: CHECK CURRENT STORAGE ---
        current_stock_kg = get_current_warehouse_stock()

        # --- STEP 2: PREDICT FUTURE FLOW (Separate models for I/O) ---

        # 2a. Supply Forecast (What the farmers will deliver)
        df_supply = pd.read_sql("SELECT date as ds, net_weight_kg as y FROM transactions", engine)
        m_supply = Prophet().fit(df_supply)
        future_supply = m_supply.predict(m_supply.make_future_dataframe(periods=30))

        # FIX: Assign INFLOW. Must cast Prophet/Pandas sum to float() for compatibility with current_stock_kg
        predicted_inflow = float(future_supply.tail(30)['yhat'].sum())

        # 2b. Demand Forecast (What the factory will use)
        df_demand = pd.read_sql("SELECT date as ds, kilos_processed as y FROM production_logs", engine)
        m_demand = Prophet().fit(df_demand)
        future_demand = m_demand.predict(m_demand.make_future_dataframe(periods=30))

        # FIX: Assign OUTFLOW. Must cast Prophet/Pandas sum to float()
        predicted_outflow = float(future_demand.tail(30)['yhat'].sum())

        # --- STEP 3: CALCULATE PROJECTED BALANCE ---
        # Current Stock + Predicted Inflow - Predicted Outflow

        # FIX: Ensure Current Stock (from get_current_warehouse_stock()) is treated as a float
        # for the final calculation, though the helper function should handle this.
        # It is safest to cast current_stock_kg here as well.
        projected_balance = (float(current_stock_kg) + predicted_inflow) - predicted_outflow

        # --- STEP 4: DECISION LOGIC ---
        safety_buffer = 150  # Always keep at least 150kg on hand


        # SCENARIO A: We have a healthy surplus
        if projected_balance >= safety_buffer:
            return {
                "status": "HEALTHY",
                "message": "No orders needed. Projected surplus is sufficient.",
                "analysis": {
                    "current_storage": int(current_stock_kg),
                    "projected_end_stock": int(projected_balance),
                    "predicted_deficit_if_empty_now": int(predicted_outflow - predicted_inflow)
                }
            }

        # SCENARIO B: We are running low (CRITICAL)
        true_deficit = (safety_buffer - projected_balance)  # How much we need to buy to hit the buffer

        # Get Top Ranked Suppliers (based on the score calculated in scoring_engine.py)
        top_suppliers = pd.read_sql("""
            SELECT supplier_id, name, ai_reliability_score, farm_profile 
            FROM supplier_profiles 
            ORDER BY ai_reliability_score DESC LIMIT 3
        """, engine).to_dict(orient="records")

        # Distribute the order amount
        suggested_orders = []
        order_per_supplier = true_deficit / len(top_suppliers)

        for s in top_suppliers:
            suggested_orders.append({
                "supplier": s['name'],
                "rank_score": s['ai_reliability_score'],
                "suggested_order_kg": int(order_per_supplier),
                "reason": "Top performer selected to mitigate projected stock shortage."
            })

        return {
            "status": "CRITICAL_ORDERING_REQUIRED",
            "message": f"Projected stock will fall below safety buffer of {safety_buffer}kg.",
            "analysis": {
                "current_storage": int(current_stock_kg),
                "predicted_usage_spike": int(predicted_outflow),
                "required_purchase_kg": int(true_deficit)
            },
            "ai_suggestion": suggested_orders
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}



def get_current_warehouse_stock():
    """
    Calculates Real-Time Stock, ENSURING result is a standard FLOAT.
    """
    sql_query = """
    SELECT
        (COALESCE(SUM(T.net_weight_kg), 0) - COALESCE(SUM(P.kilos_processed), 0)) AS current_stock_kg
    FROM transactions T
    FULL JOIN production_logs P ON 1=1;
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        current_stock = result.scalar() or 0.0

    # FIX: Explicitly convert the high-precision Decimal to a standard float
    return float(max(0, current_stock))