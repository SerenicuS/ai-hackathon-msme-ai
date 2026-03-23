# Cacao MSME Management API

> Smart cacao supply chain management system with AI-powered supplier scoring, demand forecasting, and intelligent inventory management.

**Built with:** Bun + Elysia + Prisma + TypeScript

---

## Features

### 1. **Supplier Scoring System**
- Automatically scores suppliers based on:
  - **Seasonality** (40%): Delivery recency
  - **Volume** (30%): Delivered vs expected yield
  - **Quality** (20%): Audit results (mold, insects, moisture)
  - **PhilGAP Certification** (10%): Compliance status
- Real-time leaderboard with ranked suppliers

### 2. **Demand Forecasting**
- Historical trend analysis using linear regression
- 30-day demand prediction
- Helps anticipate future inventory needs

### 3. **Smart Inventory Management**
- Real-time stock calculation
- Predicts inflow and outflow
- Automatic order suggestions when stock falls below safety buffer (2000kg)
- Distributes orders among top-ranked suppliers

### 4. **Utility Tools**
- **Database Seeder**: Populate with realistic test data (12 suppliers, 120 days history)
- **Consumer Simulator**: Interactive CLI to simulate production consumption

---

## Project Structure

```
ts-src/bun-elysia-app/
├── prisma/
│   └── schema.prisma          # Database schema
├── src/
│   ├── index.ts              # Main application entry
│   ├── routes.ts             # Route aggregation
│   ├── config/
│   │   └── database.ts       # Prisma client singleton
│   ├── types/
│   │   └── index.ts          # Shared TypeScript types
│   ├── suppliers/
│   │   ├── controller.ts     # Supplier routes
│   │   ├── service.ts        # Scoring engine logic
│   │   └── model.ts          # Supplier schemas
│   ├── forecasting/
│   │   ├── controller.ts     # Forecasting routes
│   │   ├── service.ts        # Prediction algorithms
│   │   └── model.ts          # Forecast schemas
│   ├── inventory/
│   │   ├── controller.ts     # Inventory routes
│   │   ├── service.ts        # Order suggestion logic
│   │   └── model.ts          # Inventory schemas
│   ├── utils/
│   │   └── seeder.ts         # Database seeding script
│   └── scripts/
│       └── consumer.ts       # Production consumption simulator
├── package.json
├── tsconfig.json
└── .env.example
```

---

## Getting Started

### Prerequisites

- **Bun** runtime installed ([bun.sh](https://bun.sh))
- **PostgreSQL** database (local or cloud like [Neon.tech](https://neon.tech))

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd ts-src/bun-elysia-app
   ```

2. **Install dependencies:**
   ```bash
   bun install
   ```

3. **Setup environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your PostgreSQL connection string:
   ```env
   DATABASE_URL="postgresql://user:password@host:5432/database?sslmode=require"
   ```

4. **Push database schema:**
   ```bash
   bun run db:push
   ```

   This creates the tables: `suppliers`, `transactions`, `production_logs`

5. **Seed the database with test data:**
   ```bash
   bun run seed
   ```

   This populates:
   - 12 Davao City cacao suppliers
   - 120 days of transaction history
   - Production logs showing declining inventory

---

## Running the Application

### Start the API server:
```bash
bun run dev
```

The server starts at **http://localhost:8080**

### Access API Documentation:
Visit **http://localhost:8080/openapi** for interactive Swagger UI

---

## API Endpoints

### 1. Update Supplier Scores
**Endpoint:** `POST /api/v1/suppliers/update-scores`

Calculates and updates all supplier reliability scores, then returns the leaderboard.

**Response:**
```json
{
  "status": "success",
  "message": "Supplier scores updated and fetched.",
  "data": [
    {
      "supplier_id": "SUP-DVO-010",
      "name": "Mount Apo Foothill Coop",
      "location": { "city": "Davao City", "district": "Calinan", "area": "Cawayan" },
      "reliability_score": 95,
      "description": { "bearing_trees": 10000, ... },
      "eligibility": { "philgap_certified": true, ... }
    }
  ]
}
```

---

### 2. Predict Demand
**Endpoint:** `GET /api/v1/forecasting/predict-demand`

Predicts total cacao demand for the next 30 days using historical trends.

**Response:**
```json
{
  "status": "success",
  "forecast_total_kg": 4800,
  "message": "Prediction complete based on historical trend analysis."
}
```

---

### 3. Suggest Orders
**Endpoint:** `GET /api/v1/inventory/suggest-orders`

Analyzes current stock, predicts flow, and suggests orders if needed.

**Response (Healthy):**
```json
{
  "status": "HEALTHY",
  "message": "No orders needed. Projected surplus is sufficient.",
  "analysis": {
    "current_storage": 3500,
    "projected_end_stock": 2800,
    "required_purchase_kg": 0
  }
}
```

**Response (Critical):**
```json
{
  "status": "CRITICAL_ORDERING_REQUIRED",
  "message": "Projected stock will fall below safety buffer of 2000kg.",
  "analysis": {
    "current_storage": 1200,
    "predicted_usage_spike": 4500,
    "required_purchase_kg": 1300
  },
  "ai_suggestion": [
    {
      "supplier": "Mount Apo Foothill Coop",
      "rank_score": 95,
      "suggested_order_kg": 433,
      "reason": "Top performer selected to mitigate projected stock shortage."
    }
  ]
}
```

---

## Utility Scripts

### 1. Database Seeder
Populates the database with realistic test data.

```bash
bun run seed
```

**What it creates:**
- 12 cacao suppliers from Davao City
- 120 days of purchase transactions
- Production logs with declining inventory trend
- Configured to trigger "CRITICAL" ordering state

---

### 2. Consumer Simulator
Interactive CLI tool to simulate production consumption in real-time.

```bash
bun run consumer
```

**Features:**
- Manual product entry (5 product types with different weights)
- Auto-drain mode for continuous simulation
- Direct database updates
- Real-time stock depletion

**Menu:**
```
[1] Dark Chocolate Bar     (-0.05kg)
[2] Tablea Pack           (-0.2kg)
[3] Cocoa Powder          (-0.5kg)
[4] ⚠️ DEMO NUKE (Crisis)  (-500kg)
[5] 🔄 AUTO-DRAIN         (Custom rate)
[Q] Quit
```

---

## Development Workflow

### View Database in GUI:
```bash
bun run db:studio
```
Opens Prisma Studio at http://localhost:5555

### Regenerate Prisma Client:
```bash
bun run db:generate
```

### Update Database Schema:
1. Edit `prisma/schema.prisma`
2. Run `bun run db:push` to apply changes

---

## Database Schema

### Suppliers Table
- `supplier_id` (PK): Unique identifier
- `name`: Supplier business name
- `location`: JSON (city, district, area)
- `eligibility`: JSON (PhilGAP certification)
- `description`: JSON (farm details)
- `reliability_score`: Calculated score (0-100)

### Transactions Table
- `transaction_id` (PK): Unique identifier
- `supplier_id` (FK): Links to supplier
- `amount`: Quantity in kg
- `price`: Price per unit
- `date`: Transaction date
- `quality`: JSON (audit results)
- `status`: Transaction status

### Production_logs Table
- `log_id` (PK): Unique identifier
- `date`: Production date
- `product_type`: Product name
- `quantity`: Amount consumed in kg
- `supplier_id` (FK): Source supplier

---

## Scoring Algorithm

The supplier scoring engine uses a weighted formula:

```
Final Score = (Seasonality × 0.40) + 
              (Volume × 0.30) + 
              (Quality × 0.20) + 
              (PhilGAP × 0.10)
```

**Seasonality:**
- `max(0, 100 - (days_since_last_delivery × 2))`
- Penalizes inactive suppliers

**Volume:**
- `min(100, (total_delivered / expected_yield) × 100)`
- Expected yield = bearing_trees × 2.0 kg

**Quality:**
- Starts at 100
- -40 points if mold > 3%
- -20 points if insect damage > 2.5%
- -20 points if moisture > 8%

**PhilGAP:**
- 100 if certified
- 0 if not certified

---

## Forecasting Method

Uses **linear regression** instead of Prophet for simplicity:

1. Convert historical data to time series
2. Calculate regression line
3. Project 30 days into the future
4. Ensure non-negative predictions with `max(0, value)`

**Note:** This is a simplified approach. For production systems, consider more sophisticated methods like ARIMA, Prophet, or LSTM models.

---

## API vs Python Backend

### Original Python (FastAPI)
```
POST /update-scores
GET /predict-demand
GET /suggest-orders-smart
```

### New TypeScript (Elysia)
```
POST /api/v1/suppliers/update-scores
GET /api/v1/forecasting/predict-demand
GET /api/v1/inventory/suggest-orders
```

**Key Differences:**
- Module-based URL structure (`/api/v1/module/action`)
- Standard HTTP status codes (400, 500) instead of `{status: "error"}`
- Type-safe schemas with automatic OpenAPI generation
- Faster runtime with Bun (3-4x faster than Node.js)

---

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
bun run db:studio
```

If failed, verify:
- DATABASE_URL is correct in `.env`
- PostgreSQL server is running
- Network/firewall allows connections

### Prisma Client Errors
```bash
# Regenerate Prisma Client
bun run db:generate
```

### TypeScript Errors
```bash
# Check for type issues
bun run src/index.ts
```

---

## Performance Optimization

- **Bun Runtime**: 3-4x faster than Node.js
- **Prisma Queries**: Optimized with proper indexes
- **Batch Operations**: Scoring updates use transactions
- **Connection Pooling**: Automatic with Prisma

---

## Contributing

This project follows the existing Elysia module pattern:
1. Each feature gets its own module folder
2. Module structure: `controller.ts`, `service.ts`, `model.ts`
3. Controllers handle HTTP, Services contain business logic
4. Models define Elysia schemas and TypeScript types

---

## License

This project is part of the AI Hackathon MSME AI initiative.

---

## Support

For issues or questions:
- Check the OpenAPI docs at `/openapi`
- Review the code comments
- Test with the seeder and consumer scripts

---

**Built with ❤️ using Bun, Elysia, and Prisma**
