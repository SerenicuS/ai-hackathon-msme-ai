// Forecasting controller - Routes for demand forecasting
// Translates /predict-demand endpoint from main.py

import { Elysia } from "elysia";
import { ForecastingService } from "./service";
import { forecastingModel } from "./model";

const service = new ForecastingService();

export const forecastingRoutes = new Elysia({
  prefix: "forecasting",
  tags: ["Forecasting"],
})
  /**
   * GET /api/v1/forecasting/predict-demand
   * Predicts demand for the next 30 days using linear regression
   * Translates from GET /predict-demand in main.py
   */
  .get(
    "/predict-demand",
    async ({ set }) => {
      try {
        const forecast = await service.predictDemand();
        
        if (forecast.status === "warning") {
          set.status = 400;
        }
        
        return forecast;
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
        200: forecastingModel.predictDemandResponse,
        400: forecastingModel.predictDemandResponse,
        500: forecastingModel.errorResponse,
      },
      detail: {
        summary: "Predict future demand",
        description:
          "Analyzes historical transaction data and predicts total demand for the next 30 days using linear regression analysis.",
      },
    }
  );
