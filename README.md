# AI Hackathon MSME AI - Cacao Supply Chain Management

This project contains both Python and TypeScript implementations of a smart cacao supply chain management system.

## 🚀 Quick Start

### TypeScript Implementation (Recommended)

The TypeScript version is located in `ts-src/bun-elysia-app/` and features:

- ⚡ **3-4x faster** than the Python version (Bun runtime)
- 🔒 **Type-safe** with full TypeScript support
- 📚 **Auto-generated API docs** (OpenAPI/Swagger)
- 🛠️ **Better tooling** with Prisma ORM

**Get started:**

```bash
cd ts-src/bun-elysia-app
bun install
cp .env.example .env
# Edit .env with your DATABASE_URL
bun run db:push
bun run seed
bun run dev
```

Visit <http://localhost:8080/openapi> for API documentation

**Full documentation:** [ts-src/bun-elysia-app/README.md](ts-src/bun-elysia-app/README.md)

---

### Python Implementation (Original)

The Python version uses FastAPI and is located in the root directory.

**Requirements:**

```bash
pip install fastapi uvicorn pandas sqlalchemy psycopg2-binary prophet python-dotenv
```

**Run:**

```bash
uvicorn main:app --reload
```

**Endpoints:**

1. `POST /update-scores` - Update supplier reliability scores
2. `GET /predict-demand` - Forecast 30-day demand using Prophet
3. `GET /suggest-orders-smart` - AI-powered order suggestions

---

## 📊 Features

### 1. Supplier Scoring System

- Weighted algorithm: Seasonality (40%), Volume (30%), Quality (20%), PhilGAP (10%)
- Real-time leaderboard
- Historical trend analysis

### 2. Demand Forecasting

- Python: Facebook Prophet (ML-based)
- TypeScript: Linear regression (statistical)
- 30-day projections

### 3. Smart Inventory Management

- Real-time stock tracking
- Automatic order suggestions
- Safety buffer monitoring (2000kg threshold)
- Top supplier recommendations

### 4. Utility Tools

- **Seeder**: Populate database with realistic test data
- **Consumer Simulator**: Interactive CLI for production simulation

---

## 🏗️ Architecture

### Database Schema

- **Suppliers**: Farm details, location, certification, reliability scores
- **Transactions**: Purchase records, quality audits
- **Production Logs**: Manufacturing consumption history

### Technology Stack

**Python Backend:**

- FastAPI
- SQLAlchemy
- Prophet (ML forecasting)
- PostgreSQL

**TypeScript Backend:**

- Bun runtime
- Elysia framework
- Prisma ORM
- simple-statistics
- PostgreSQL

---

## 📁 Project Structure

```
.
├── main.py                    # Python FastAPI application
├── scoring_engine.py          # Supplier scoring logic
├── seeder.py                  # Python database seeder
├── pseudo_consumer.py         # Python consumption simulator
├── db_schema.sql             # Database schema
├── data.json                 # Sample data
└── ts-src/
    └── bun-elysia-app/       # TypeScript implementation
        ├── prisma/
        │   └── schema.prisma # Database schema
        ├── src/
        │   ├── suppliers/    # Scoring module
        │   ├── forecasting/  # Prediction module
        │   ├── inventory/    # Order management
        │   ├── utils/        # Seeder script
        │   └── scripts/      # Consumer CLI
        └── README.md         # Detailed TS docs
```

---

## 🔄 API Comparison

| Feature        | Python (FastAPI)            | TypeScript (Elysia)                      |
| -------------- | --------------------------- | ---------------------------------------- |
| Update Scores  | `POST /update-scores`       | `POST /api/v1/suppliers/update-scores`   |
| Predict Demand | `GET /predict-demand`       | `GET /api/v1/forecasting/predict-demand` |
| Suggest Orders | `GET /suggest-orders-smart` | `GET /api/v1/inventory/suggest-orders`   |
| Runtime        | uvicorn (Node ~)            | Bun (3-4x faster)                        |
| Type Safety    | ❌                          | ✅ Full TypeScript                       |
| API Docs       | Manual                      | Auto-generated OpenAPI                   |

---

## 🧪 Testing

### Seed the Database

**Python:**

```bash
python seeder.py
```

**TypeScript:**

```bash
cd ts-src/bun-elysia-app
bun run seed
```

### Run Consumer Simulator

**Python:**

```bash
python pseudo_consumer.py
```

**TypeScript:**

```bash
cd ts-src/bun-elysia-app
bun run consumer
```

### Test API

**Python:**

```bash
python test_api.py
```

**TypeScript:** Use the Swagger UI at <http://localhost:8080/openapi>

---

## 🌐 Environment Setup

Create a `.env` file in the root directory:

```env
DATABASE_URL='postgresql://user:password@host:5432/database?sslmode=require'
```

For the TypeScript version, also create `ts-src/bun-elysia-app/.env`

---

## 📈 Scoring Algorithm

```
Final Score = (Seasonality × 0.40) +
              (Volume × 0.30) +
              (Quality × 0.20) +
              (PhilGAP × 0.10)
```

**Seasonality:** `max(0, 100 - (days_since_last_delivery × 2))`
**Volume:** `min(100, (total_delivered / expected_yield) × 100)`
**Quality:** Deductions for mold, insects, moisture
**PhilGAP:** Binary (100 if certified, 0 if not)

---

## 🎯 Use Cases

1. **Supplier Management**: Track and rank cacao suppliers
2. **Quality Control**: Monitor audit results and compliance
3. **Inventory Planning**: Predict shortages before they occur
4. **Order Optimization**: Automatically suggest best suppliers to order from
5. **Real-time Monitoring**: Simulate and track production in real-time

---

## 🛠️ Development

### Python

```bash
# Install dependencies
pip install -r requirements.txt  # Create this if needed

# Run development server
uvicorn main:app --reload --port 8000
```

### TypeScript

```bash
cd ts-src/bun-elysia-app

# Development mode with hot reload
bun run dev

# View database
bun run db:studio

# Update schema
bun run db:push
```

---

## 📝 License

This project is part of the AI Hackathon MSME AI initiative.

---

## 🤝 Contributing

Both implementations follow their respective best practices:

- **Python**: Follow PEP 8 style guide
- **TypeScript**: ESLint + Prettier, module-based architecture

---

## 📚 Documentation

- **TypeScript Full Docs**: [ts-src/bun-elysia-app/README.md](ts-src/bun-elysia-app/README.md)
- **API Reference**: Visit `/openapi` endpoint when server is running
- **Database Schema**: See `db_schema.sql` or `prisma/schema.prisma`

---

**Built for efficient cacao supply chain management in Davao City and beyond! 🍫**
