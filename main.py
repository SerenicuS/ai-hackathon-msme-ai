import os
import pandas as pd
from fastapi import FastAPI
from sqlalchemy import create_engine
from prophet import Prophet
import scoring_engine  # This imports the file you just made!
from sqlalchemy import text  # Make sure this is imported at the top
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Database Connection (from environment variable)
# !!pip install python-dotenv!!
db_str = os.getenv('DATABASE_URL')
if not db_str:
    raise ValueError("DATABASE_URL environment variable is not set")
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
        # 🟢 FIX: Replaced non-existent 'compliance_status' with 'eligibility'
        query = """
            SELECT supplier_id, name, location, reliability_score, 
                   description  , eligibility
            FROM suppliers
            ORDER BY reliability_score DESC
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

        # 2a. Supply Forecast
        df_supply = pd.read_sql("SELECT date as ds, amount as y FROM transactions", engine)
        if len(df_supply) >= 2:
            m_supply = Prophet().fit(df_supply)
            future_supply = m_supply.predict(m_supply.make_future_dataframe(periods=30))
            # FIX 1: Use max(0, ...) to prevent negative predictions
            predicted_inflow = max(0.0, float(future_supply.tail(30)['yhat'].sum()))
        else:
            predicted_inflow = 0.0

        # 2b. Demand Forecast
        df_demand = pd.read_sql("SELECT date as ds, quantity as y FROM production_logs", engine)
        if len(df_demand) >= 2:
            m_demand = Prophet().fit(df_demand)
            future_demand = m_demand.predict(m_demand.make_future_dataframe(periods=30))
            # FIX 1: Use max(0, ...) to prevent negative predictions
            predicted_outflow = max(0.0, float(future_demand.tail(30)['yhat'].sum()))
        else:
            predicted_outflow = 0.0

        # --- STEP 3: CALCULATE PROJECTED BALANCE ---
        # Current Stock + Predicted Inflow - Predicted Outflow
        projected_balance = (float(current_stock_kg) + predicted_inflow) - predicted_outflow

        # --- STEP 4: DECISION LOGIC ---
        # FIX 2: Raise Safety Buffer to 2,000kg (approx 40 sacks).
        # 150kg is too small for a factory; 2000kg makes "1633kg" validly CRITICAL.
        safety_buffer = 2000

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
        true_deficit = (safety_buffer - projected_balance)

        # Get Top Ranked Suppliers
        top_suppliers = pd.read_sql("""
            SELECT name, reliability_score 
            FROM suppliers 
            ORDER BY reliability_score DESC LIMIT 3
        """, engine).to_dict(orient="records")

        # Distribute the order amount
        suggested_orders = []
        # Ensure we don't divide by zero if no suppliers found
        if top_suppliers:
            order_per_supplier = true_deficit / len(top_suppliers)
            for s in top_suppliers:
                suggested_orders.append({
                    "supplier": s['name'],
                    "rank_score": s['reliability_score'],
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
    Calculates Real-Time Stock by summing inputs and outputs separately.
    """
    # We use two separate subqueries to avoid multiplying the rows
    sql_query = """
        SELECT 
            (SELECT COALESCE(SUM(amount), 0) FROM transactions) - 
            (SELECT COALESCE(SUM(quantity), 0) FROM production_logs) 
        as current_stock_kg
        """
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        current_stock = result.scalar() or 0.0

    return float(max(0, current_stock))