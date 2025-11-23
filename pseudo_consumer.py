import time
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
import os
import sys

# ==========================================
# 1. CONFIGURATION (Direct to Cloud)
# ==========================================
DB_STR = 'postgresql://neondb_owner:npg_VhvNzRaM3xi8@ep-young-fire-a1mrxhwn-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

try:
    engine = create_engine(DB_STR)
    print("✅ Connected to Cloud Database successfully.")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    input("Press Enter to exit...")
    exit()

# The Menu
MENU = {
    "1": {"name": "Dark Chocolate Bar", "weight": 0.05},
    "2": {"name": "Tablea Pack", "weight": 0.20},
    "3": {"name": "Cocoa Powder", "weight": 0.50},
    "4": {"name": "⚠️ DEMO NUKE (Crisis)", "weight": 500.0},
    "5": {"name": "🔄 AUTO-DRAIN (Real-Time Sim)", "mode": "auto"}  # <--- NEW FEATURE
}

# Dummy supplier logic to satisfy your DB constraints
# (We just pick the first one to avoid Foreign Key errors)
DEFAULT_SUPPLIER_ID = "SUP-DVO-001"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def log_usage_to_db(product_name, quantity_kg, silent=False):
    """
    Inserts a record directly into the production_logs table.
    """
    unique_id = f"LIVE-{uuid.uuid4().hex[:8]}"

    query = text("""
        INSERT INTO production_logs (log_id, date, product_type, quantity, supplier_id)
        VALUES (:log_id, :date, :product_type, :quantity, :supplier_id)
    """)

    try:
        with engine.begin() as conn:
            conn.execute(query, {
                "log_id": unique_id,
                "date": datetime.now(),
                "product_type": product_name,
                "quantity": quantity_kg,
                "supplier_id": DEFAULT_SUPPLIER_ID,  # Hardcoded to prevent crashes
            })
        if not silent:
            print(f"🚀 SENT: -{quantity_kg}kg ({product_name})")
        return True
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        return False


def run_auto_drain():
    """
    The 'Real-Time' Loop Feature
    """
    print("\n--- 🔄 AUTO-DRAIN CONFIGURATION ---")
    try:
        kg_per_tick = float(input("   🔥 How many KG to burn per tick? (e.g., 2): "))
        speed_sec = float(input("   ⏱️  How many seconds per tick? (e.g., 1): "))

        print(f"\n✅ STARTING SIMULATION: Burning {kg_per_tick}kg every {speed_sec} seconds.")
        print("🔴 PRESS 'CTRL + C' TO STOP THE DRAIN...\n")
        time.sleep(1)

        counter = 1
        while True:
            success = log_usage_to_db("Continuous Production", kg_per_tick, silent=True)
            if success:
                # Cool Visual Feedback
                sys.stdout.write(f"\r[{counter}] 🔥 Burned {kg_per_tick}kg... Stock Dropping... ")
                sys.stdout.flush()
                counter += 1
            time.sleep(speed_sec)

    except KeyboardInterrupt:
        print("\n\n🛑 SIMULATION STOPPED. Returning to menu...")
        time.sleep(2)


def main():
    while True:
        clear_screen()
        print("╔═══════════════════════════════════════════╗")
        print("║   🏭 LIVE CONSUMPTION TERMINAL (DIRECT)   ║")
        print("╚═══════════════════════════════════════════╝")
        print(f"☁️  Linked to: NeonDB (ep-young-fire...)\n")

        print("SELECT ACTION:")
        for key, item in MENU.items():
            if "weight" in item:
                print(f" [{key}] {item['name']} \t(-{item['weight']}kg)")
            else:
                print(f" [{key}] {item['name']}")  # For the Auto-Drain option

        print("\n[Q] Quit")

        choice = input("\n👉 ENTER COMMAND: ").upper()

        if choice == 'Q':
            break

        if choice in MENU:
            selected = MENU[choice]

            # CHECK IF IT IS THE SPECIAL 'AUTO' MODE
            if selected.get("mode") == "auto":
                run_auto_drain()
                continue

            # STANDARD MANUAL MODE
            try:
                qty = int(input(f"📦 Quantity of '{selected['name']}': "))
                total_kg = qty * selected['weight']
                print(f"\n⏳ Syncing with Cloud for {total_kg}kg deduction...")
                log_usage_to_db(selected['name'], total_kg)
                time.sleep(1.5)
            except ValueError:
                print("❌ Invalid Number")
                time.sleep(1)


if __name__ == "__main__":
    main()