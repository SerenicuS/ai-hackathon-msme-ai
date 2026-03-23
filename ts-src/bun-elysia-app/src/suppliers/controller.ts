// Suppliers controller - Routes for supplier management
// Translates /update-scores endpoint from main.py

import { Elysia } from "elysia";
import { SupplierService } from "./service";
import { supplierModel } from "./model";

const service = new SupplierService();

export const supplierRoutes = new Elysia({
  prefix: "suppliers",
  tags: ["Suppliers"],
})
  /**
   * POST /api/v1/suppliers/update-scores
   * Triggers scoring calculation and returns updated leaderboard
   * Translates from POST /update-scores in main.py
   */
  .post(
    "/update-scores",
    async ({ set }) => {
      try {
        console.log("Received signal: Updating Supplier Scores...");

        // STEP 1: Run the scoring engine to update the DB
        await service.calculateScores();

        // STEP 2: Fetch the fresh leaderboard data
        const leaderboard = await service.getLeaderboard();

        // STEP 3: Return the updated leaderboard
        return {
          status: "success",
          message: "Supplier scores updated and fetched.",
          data: leaderboard,
        };
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
        200: supplierModel.updateScoresResponse,
        500: supplierModel.errorResponse,
      },
      detail: {
        summary: "Update supplier reliability scores",
        description:
          "Calculates and updates supplier scores based on seasonality, volume, quality, and PhilGAP certification. Returns updated leaderboard sorted by score.",
      },
    }
  );
