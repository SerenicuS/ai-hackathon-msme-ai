#!/usr/bin/env bun
// Database seeder utility
// Translates seeder.py to TypeScript

import { prisma } from "../config/database";

/**
 * Clean old transactional data (starting fresh)
 */
async function cleanTransactionalData() {
  console.log("0. Cleaning old transactional data (starting fresh)...");
  
  // Delete in correct order due to foreign key constraints
  await prisma.productionLog.deleteMany({});
  await prisma.transaction.deleteMany({});
  
  console.log("✅ Old transactions and logs deleted.");
}

/**
 * Seed suppliers with realistic Davao City cacao farm data
 */
async function seedSuppliers() {
  const suppliers = [
    {
      supplier_id: "SUP-DVO-001",
      name: "Davao Golden Cacao Coop",
      location: { city: "Davao City", district: "Calinan", area: "Wangan" },
      eligibility: { philgap_certified: true, philgap_id: "BPI-2023-11" },
      description: {
        bearing_trees: 2000,
        total_hectares: 5.0,
        elevation_meters: 450,
        soil_type: "loamy",
        annual_rainfall_mm: 1800,
      },
      reliability_score: 85,
    },
    {
      supplier_id: "SUP-DVO-099",
      name: "Baguio District Aggregators",
      location: { city: "Davao City", district: "Baguio", area: "Tawan-Tawan" },
      eligibility: { philgap_certified: false },
      description: {
        bearing_trees: 500,
        total_hectares: 2.0,
        elevation_meters: 450,
        soil_type: "loamy",
        annual_rainfall_mm: 1800,
      },
      reliability_score: 65,
    },
    {
      supplier_id: "SUP-DVO-002",
      name: "Malagos Valley Growers",
      location: { city: "Davao City", district: "Baguio", area: "Malagos" },
      eligibility: { philgap_certified: true, philgap_id: "BPI-2024-01" },
      description: {
        bearing_trees: 5000,
        total_hectares: 8.0,
        elevation_meters: 350,
        soil_type: "volcanic loam",
        annual_rainfall_mm: 2100,
      },
      reliability_score: 92,
    },
    {
      supplier_id: "SUP-DVO-003",
      name: "Paquibato Highland Farms",
      location: { city: "Davao City", district: "Paquibato", area: "Malabog" },
      eligibility: { philgap_certified: false },
      description: {
        bearing_trees: 800,
        total_hectares: 1.5,
        elevation_meters: 700,
        soil_type: "clay-loam",
        annual_rainfall_mm: 1750,
      },
      reliability_score: 70,
    },
    {
      supplier_id: "SUP-DVO-004",
      name: "Tugbok Cacao Alliance",
      location: { city: "Davao City", district: "Tugbok", area: "Mintal" },
      eligibility: { philgap_certified: true, philgap_id: "BPI-2023-05" },
      description: {
        bearing_trees: 3500,
        total_hectares: 6.0,
        elevation_meters: 200,
        soil_type: "sandy loam",
        annual_rainfall_mm: 1900,
      },
      reliability_score: 88,
    },
    {
      supplier_id: "SUP-DVO-005",
      name: "Toril Eco-Agri Ventures",
      location: { city: "Davao City", district: "Toril", area: "Eden" },
      eligibility: { philgap_certified: false },
      description: {
        bearing_trees: 1200,
        total_hectares: 3.0,
        elevation_meters: 800,
        soil_type: "volcanic",
        annual_rainfall_mm: 2200,
      },
      reliability_score: 78,
    },
    {
      supplier_id: "SUP-DVO-006",
      name: "Marilog Indigenous Farmers",
      location: { city: "Davao City", district: "Marilog", area: "Baganihan" },
      eligibility: { philgap_certified: true, philgap_id: "BPI-2024-03" },
      description: {
        bearing_trees: 600,
        total_hectares: 2.0,
        elevation_meters: 1100,
        soil_type: "limestone rich",
        annual_rainfall_mm: 1650,
      },
      reliability_score: 75,
    },
    {
      supplier_id: "SUP-DVO-007",
      name: "Tigatto Riverbank Cacao",
      location: { city: "Davao City", district: "Buhangin", area: "Tigatto" },
      eligibility: { philgap_certified: true, philgap_id: "BPI-2023-12" },
      description: {
        bearing_trees: 1500,
        total_hectares: 2.5,
        elevation_meters: 100,
        soil_type: "alluvial",
        annual_rainfall_mm: 1850,
      },
      reliability_score: 82,
    },
    {
      supplier_id: "SUP-DVO-008",
      name: "Subasta Integrated Farms",
      location: { city: "Davao City", district: "Calinan", area: "Subasta" },
      eligibility: { philgap_certified: true, philgap_id: "BPI-2022-09" },
      description: {
        bearing_trees: 4000,
        total_hectares: 7.5,
        elevation_meters: 400,
        soil_type: "loamy",
        annual_rainfall_mm: 2000,
      },
      reliability_score: 90,
    },
    {
      supplier_id: "SUP-DVO-009",
      name: "Matina Small Holders",
      location: { city: "Davao City", district: "Talomo", area: "Matina Pangi" },
      eligibility: { philgap_certified: false },
      description: {
        bearing_trees: 300,
        total_hectares: 1.0,
        elevation_meters: 50,
        soil_type: "silt loam",
        annual_rainfall_mm: 1950,
      },
      reliability_score: 60,
    },
    {
      supplier_id: "SUP-DVO-010",
      name: "Mount Apo Foothill Coop",
      location: { city: "Davao City", district: "Calinan", area: "Cawayan" },
      eligibility: { philgap_certified: true, philgap_id: "BPI-2024-05" },
      description: {
        bearing_trees: 10000,
        total_hectares: 20.0,
        elevation_meters: 550,
        soil_type: "volcanic loam",
        annual_rainfall_mm: 2300,
      },
      reliability_score: 95,
    },
    {
      supplier_id: "SUP-DVO-011",
      name: "Acacia Farm Agri-Ventures",
      location: { city: "Davao City", district: "Sasa", area: "Panacan" },
      eligibility: { philgap_certified: false },
      description: {
        bearing_trees: 1800,
        total_hectares: 4.0,
        elevation_meters: 80,
        soil_type: "clay-rich",
        annual_rainfall_mm: 1700,
      },
      reliability_score: 72,
    },
  ];

  console.log("1. Inserting Suppliers...");

  for (const supplier of suppliers) {
    await prisma.supplier.upsert({
      where: { supplier_id: supplier.supplier_id },
      update: supplier,
      create: supplier,
    });
  }

  console.log("✅ Suppliers added/updated.");
  return suppliers.map((s) => s.supplier_id);
}

/**
 * Seed transactions with historical data (120 days)
 */
async function seedTransactions(supplierIds: string[]) {
  const transactions = [];
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 120); // 4 months history

  // 1. THE BIG STARTER PACK - Initial large delivery
  transactions.push({
    transaction_id: "TXN-START-000",
    supplier_id: supplierIds[0],
    date: startDate,
    amount: 4500, // Large initial amount
    price: 120.0,
    quality: { moisture: 7.0 },
    status: "completed",
  });

  // 2. REGULAR DELIVERIES - Every 10 days
  let currentDeliveryDate = new Date(startDate);
  currentDeliveryDate.setDate(currentDeliveryDate.getDate() + 5);
  let txnCount = 1;
  const now = new Date();

  while (currentDeliveryDate < now) {
    const amount = Math.floor(Math.random() * (450 - 350 + 1)) + 350; // 350-450kg

    transactions.push({
      transaction_id: `TXN-AUTO-${txnCount}`,
      supplier_id: supplierIds[txnCount % supplierIds.length],
      date: new Date(currentDeliveryDate),
      amount: amount,
      price: 125.0,
      quality: { moisture: 7.2 },
      status: "completed",
    });

    currentDeliveryDate.setDate(currentDeliveryDate.getDate() + 10);
    txnCount++;
  }

  console.log(`2. Inserting ${transactions.length} transactions...`);

  for (const transaction of transactions) {
    await prisma.transaction.create({
      data: transaction,
    });
  }

  console.log("✅ Transactions inserted.");
}

/**
 * Seed production logs with consumption history
 */
async function seedProductionLogs(supplierIds: string[]) {
  const productionLogs = [];
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 120);

  let currentSimDate = new Date(startDate);
  let logCount = 0;
  const now = new Date();

  while (currentSimDate < now) {
    // Cook on Mon, Wed, Fri (weekday 0, 2, 4)
    if ([0, 2, 4].includes(currentSimDate.getDay())) {
      const quantity = Math.floor(Math.random() * (160 - 140 + 1)) + 140; // 140-160kg

      productionLogs.push({
        log_id: `LOG-DEMO-${logCount}`,
        date: new Date(currentSimDate),
        product_type: "Dark Chocolate",
        quantity: quantity,
        supplier_id: supplierIds[logCount % supplierIds.length],
      });

      logCount++;
    }

    currentSimDate.setDate(currentSimDate.getDate() + 1);
  }

  console.log(`3. Inserting ${productionLogs.length} production logs...`);

  for (const log of productionLogs) {
    await prisma.productionLog.create({
      data: log,
    });
  }

  console.log("✅ Production logs inserted.");
}

/**
 * Main seeder function
 */
async function generateFakeData() {
  try {
    console.log("🌱 Starting database seeding...\n");

    // Step 0: Clean old data
    await cleanTransactionalData();

    // Step 1: Seed suppliers
    const supplierIds = await seedSuppliers();

    // Step 2: Seed transactions
    await seedTransactions(supplierIds);

    // Step 3: Seed production logs
    await seedProductionLogs(supplierIds);

    console.log("\n✅ DONE. Data is tuned for a 'Critical' downward trend.");
    console.log("📊 The system should show declining stock and trigger order suggestions.");
  } catch (error) {
    console.error("❌ Error during seeding:", error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

// Run the seeder
generateFakeData()
  .then(() => {
    console.log("\n🎉 Seeding completed successfully!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n💥 Seeding failed:", error);
    process.exit(1);
  });
