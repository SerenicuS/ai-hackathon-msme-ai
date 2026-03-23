// Inventory service - Smart order suggestion logic
// Translates suggest-orders-smart endpoint from main.py

import { prisma } from "../config/database";
import { ForecastingService } from "../forecasting/service";
import { OrderSuggestion, InventoryAnalysis } from "../types";

const forecastingService = new ForecastingService();

export class InventoryService {
  /**
   * Smart order suggestion system
   * Translates suggest_orders_smart() from main.py
   */
  async suggestOrders(): Promise<{
    status: string;
    message: string;
    analysis: InventoryAnalysis;
    ai_suggestion?: OrderSuggestion[];
  }> {
    try {
      // --- STEP 1: CHECK CURRENT STORAGE ---
      const currentStockKg = await this.getCurrentWarehouseStock();

      // --- STEP 2: PREDICT FUTURE FLOW (Separate models for I/O) ---
      const predictedInflow = await forecastingService.predictSupplyFlow();
      const predictedOutflow = await forecastingService.predictDemandFlow();

      // --- STEP 3: CALCULATE PROJECTED BALANCE ---
      // Current Stock + Predicted Inflow - Predicted Outflow
      const projectedBalance = currentStockKg + predictedInflow - predictedOutflow;

      // --- STEP 4: DECISION LOGIC ---
      // Safety Buffer: 2,000kg (approximately 40 sacks)
      const safetyBuffer = 2000;

      // SCENARIO A: We have a healthy surplus
      if (projectedBalance >= safetyBuffer) {
        return {
          status: "HEALTHY",
          message: "No orders needed. Projected surplus is sufficient.",
          analysis: {
            current_storage: Math.round(currentStockKg),
            projected_end_stock: Math.round(projectedBalance),
            required_purchase_kg: 0,
          },
        };
      }

      // SCENARIO B: We are running low (CRITICAL)
      const trueDeficit = safetyBuffer - projectedBalance;

      // Get Top Ranked Suppliers
      const topSuppliers = await prisma.supplier.findMany({
        select: {
          name: true,
          reliability_score: true,
        },
        orderBy: {
          reliability_score: "desc",
        },
        take: 3,
      });

      // Distribute the order amount
      const suggestedOrders: OrderSuggestion[] = [];

      if (topSuppliers.length > 0) {
        const orderPerSupplier = trueDeficit / topSuppliers.length;

        for (const supplier of topSuppliers) {
          suggestedOrders.push({
            supplier: supplier.name,
            rank_score: supplier.reliability_score,
            suggested_order_kg: Math.round(orderPerSupplier),
            reason:
              "Top performer selected to mitigate projected stock shortage.",
          });
        }
      }

      return {
        status: "CRITICAL_ORDERING_REQUIRED",
        message: `Projected stock will fall below safety buffer of ${safetyBuffer}kg.`,
        analysis: {
          current_storage: Math.round(currentStockKg),
          predicted_usage_spike: Math.round(predictedOutflow),
          required_purchase_kg: Math.round(trueDeficit),
        },
        ai_suggestion: suggestedOrders,
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Calculate real-time warehouse stock
   * Translates get_current_warehouse_stock() from main.py
   * Formula: Sum(transactions.amount) - Sum(production_logs.quantity)
   */
  async getCurrentWarehouseStock(): Promise<number> {
    try {
      // Get total inflow (transactions)
      const totalInflow = await prisma.transaction.aggregate({
        _sum: {
          amount: true,
        },
      });

      // Get total outflow (production logs)
      const totalOutflow = await prisma.productionLog.aggregate({
        _sum: {
          quantity: true,
        },
      });

      const inflowAmount = totalInflow._sum.amount || 0;
      const outflowAmount = totalOutflow._sum.quantity || 0;

      const currentStock = inflowAmount - outflowAmount;

      // Ensure non-negative stock
      return Math.max(0, currentStock);
    } catch (error) {
      console.error("Error calculating warehouse stock:", error);
      return 0;
    }
  }
}
