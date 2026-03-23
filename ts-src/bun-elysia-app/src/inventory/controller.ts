// Inventory controller - Routes for inventory management
// Translates /suggest-orders-smart endpoint from main.py

import { Elysia } from "elysia";
import { InventoryService } from "./service";
import { inventoryModel } from "./model";

const service = new InventoryService();

export const inventoryRoutes = new Elysia({
  prefix: "inventory",
  tags: ["Inventory"],
})
  /**
   * GET /api/v1/inventory/suggest-orders
   * Smart ordering system based on current stock and predicted flow
   * Translates from GET /suggest-orders-smart in main.py
   */
  .get(
    "/suggest-orders",
    async ({ set }) => {
      try {
        const suggestion = await service.suggestOrders();
        return suggestion;
      } catch (error) {
        set.status = 500;
        return {
          status: "error",
          message: error instanceof Error ? error.message : "Unknown error",
        };
      }
    },
    {
      response: {
        200: inventoryModel.suggestOrdersResponse,
        500: inventoryModel.errorResponse,
      },
      detail: {
        summary: "Get smart order suggestions",
        description:
          "Analyzes current warehouse stock, predicts future inflow/outflow, and suggests orders from top suppliers if stock will fall below safety buffer (2000kg).",
      },
    }
  );
