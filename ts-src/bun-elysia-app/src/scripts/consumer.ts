#!/usr/bin/env bun
// Production consumption simulator
// Translates pseudo_consumer.py to TypeScript
// Interactive CLI tool for simulating production usage

import { prisma } from "../config/database";

// Product menu
interface MenuItem {
  name: string;
  weight: number;
  mode?: string;
}

const MENU: { [key: string]: MenuItem } = {
  "1": { name: "Dark Chocolate Bar", weight: 0.05 },
  "2": { name: "Tablea Pack", weight: 0.2 },
  "3": { name: "Cocoa Powder", weight: 0.5 },
  "4": { name: "⚠️ DEMO NUKE (Crisis)", weight: 500.0 },
  "5": { name: "🔄 AUTO-DRAIN (Real-Time Sim)", weight: 0, mode: "auto" },
};

const DEFAULT_SUPPLIER_ID = "SUP-DVO-001";

/**
 * Clear terminal screen
 */
function clearScreen() {
  console.clear();
}

/**
 * Generate unique log ID
 */
function generateLogId(): string {
  return `LIVE-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;
}

/**
 * Log production usage to database
 */
async function logUsageToDb(
  productName: string,
  quantityKg: number,
  silent: boolean = false
): Promise<boolean> {
  try {
    const uniqueId = generateLogId();

    await prisma.productionLog.create({
      data: {
        log_id: uniqueId,
        date: new Date(),
        product_type: productName,
        quantity: quantityKg,
        supplier_id: DEFAULT_SUPPLIER_ID,
      },
    });

    if (!silent) {
      console.log(`🚀 SENT: -${quantityKg}kg (${productName})`);
    }

    return true;
  } catch (error) {
    console.error(`❌ DATABASE ERROR: ${error}`);
    return false;
  }
}

/**
 * Auto-drain simulation mode
 * Continuously burns stock at specified rate
 */
async function runAutoDrain() {
  console.log("\n--- 🔄 AUTO-DRAIN CONFIGURATION ---");

  // Get configuration from user
  const kgPerTick = parseFloat(
    prompt("   🔥 How many KG to burn per tick? (e.g., 2): ") || "2"
  );
  const speedSec = parseFloat(
    prompt("   ⏱️  How many seconds per tick? (e.g., 1): ") || "1"
  );

  console.log(
    `\n✅ STARTING SIMULATION: Burning ${kgPerTick}kg every ${speedSec} seconds.`
  );
  console.log("🔴 PRESS 'CTRL + C' TO STOP THE DRAIN...\n");

  await new Promise((resolve) => setTimeout(resolve, 1000));

  let counter = 1;
  const interval = setInterval(async () => {
    const success = await logUsageToDb(
      "Continuous Production",
      kgPerTick,
      true
    );

    if (success) {
      // Update status on same line
      process.stdout.write(
        `\r[${counter}] 🔥 Burned ${kgPerTick}kg... Stock Dropping... `
      );
      counter++;
    }
  }, speedSec * 1000);

  // Handle Ctrl+C gracefully
  process.on("SIGINT", () => {
    clearInterval(interval);
    console.log("\n\n🛑 SIMULATION STOPPED. Returning to menu...");
    setTimeout(() => {
      main();
    }, 2000);
  });
}

/**
 * Display menu and get user input
 */
function displayMenu() {
  console.log("╔═══════════════════════════════════════════╗");
  console.log("║   🏭 LIVE CONSUMPTION TERMINAL (DIRECT)   ║");
  console.log("╚═══════════════════════════════════════════╝");
  console.log(`☁️  Linked to: Database via Prisma\n`);
  console.log("SELECT ACTION:");

  for (const [key, item] of Object.entries(MENU)) {
    if (item.weight > 0) {
      console.log(`  [${key}] ${item.name} \t(-${item.weight}kg)`);
    } else {
      console.log(`  [${key}] ${item.name}`);
    }
  }

  console.log("\n  [Q] Quit");
}

/**
 * Main event loop
 */
async function main() {
  while (true) {
    clearScreen();
    displayMenu();

    const choice = (prompt("\n👉 ENTER COMMAND: ") || "").toUpperCase();

    if (choice === "Q") {
      console.log("\n👋 Goodbye!");
      await prisma.$disconnect();
      process.exit(0);
    }

    const selected = MENU[choice];

    if (!selected) {
      console.log("❌ Invalid choice");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      continue;
    }

    // CHECK IF IT IS THE SPECIAL 'AUTO' MODE
    if (selected.mode === "auto") {
      await runAutoDrain();
      continue;
    }

    // STANDARD MANUAL MODE
    try {
      const qtyInput = prompt(
        `📦 Quantity of '${selected.name}': `
      );

      if (!qtyInput) {
        continue;
      }

      const qty = parseInt(qtyInput);

      if (isNaN(qty) || qty <= 0) {
        console.log("❌ Invalid Number");
        await new Promise((resolve) => setTimeout(resolve, 1000));
        continue;
      }

      const totalKg = qty * selected.weight;
      console.log(`\n⏳ Syncing with Database for ${totalKg}kg deduction...`);
      await logUsageToDb(selected.name, totalKg);
      await new Promise((resolve) => setTimeout(resolve, 1500));
    } catch (error) {
      console.log(`❌ Error: ${error}`);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }
}

// Start the application
console.log("🔌 Connecting to database...");

prisma
  .$connect()
  .then(() => {
    console.log("✅ Connected to database successfully.\n");
    setTimeout(main, 500);
  })
  .catch((error) => {
    console.error(`❌ Connection Failed: ${error}`);
    process.exit(1);
  });
