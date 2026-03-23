// Forecasting service - Demand prediction logic
// Translates predict-demand endpoint from main.py
// Uses simple-statistics instead of Prophet for time series forecasting

import { prisma } from "../config/database";
import { linearRegression, linearRegressionLine } from "simple-statistics";
import { DataPoint } from "../types";

export class ForecastingService {
  /**
   * Predict demand for the next 30 days
   * Translates predict_demand() from main.py
   * Uses linear regression instead of Prophet
   */
  async predictDemand(): Promise<{
    status: string;
    message: string;
    forecast_total_kg?: number;
  }> {
    try {
      // 1. FETCH HISTORICAL DATA
      // Get historical consumption (date + net_weight_kg)
      const transactions = await prisma.transaction.findMany({
        select: {
          date: true,
          amount: true,
        },
        orderBy: {
          date: "asc",
        },
      });

      // Safety Check: Need at least 2 data points for prediction
      if (transactions.length < 2) {
        return {
          status: "warning",
          message: "Not enough data to train forecasting model. Add more transactions.",
          forecast_total_kg: 0,
        };
      }

      // 2. PREPARE DATA FOR REGRESSION
      // Convert dates to day indices (days since first transaction)
      const firstDate = transactions[0].date.getTime();
      const dataPoints = transactions.map((t, index) => {
        const daysSinceStart = Math.floor(
          (t.date.getTime() - firstDate) / (1000 * 60 * 60 * 24)
        );
        return [daysSinceStart, t.amount];
      });

      // 3. TRAIN MODEL: Calculate linear regression
      const regressionLine = linearRegressionLine(linearRegression(dataPoints));

      // 4. PREDICT: Project 30 days into the future
      const lastDay = dataPoints[dataPoints.length - 1][0];
      let totalPredictedDemand = 0;

      for (let day = 1; day <= 30; day++) {
        const futureDay = lastDay + day;
        const prediction = regressionLine(futureDay);
        // Prevent negative predictions
        totalPredictedDemand += Math.max(0, prediction);
      }

      return {
        status: "success",
        forecast_total_kg: Math.round(totalPredictedDemand),
        message: "Prediction complete based on historical trend analysis.",
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Predict supply inflow for the next 30 days
   * Used by inventory management for smart ordering
   */
  async predictSupplyFlow(): Promise<number> {
    try {
      const transactions = await prisma.transaction.findMany({
        select: {
          date: true,
          amount: true,
        },
        orderBy: {
          date: "asc",
        },
      });

      if (transactions.length < 2) return 0;

      const firstDate = transactions[0].date.getTime();
      const dataPoints = transactions.map((t) => {
        const daysSinceStart = Math.floor(
          (t.date.getTime() - firstDate) / (1000 * 60 * 60 * 24)
        );
        return [daysSinceStart, t.amount];
      });

      const regressionLine = linearRegressionLine(linearRegression(dataPoints));
      const lastDay = dataPoints[dataPoints.length - 1][0];

      let predictedInflow = 0;
      for (let day = 1; day <= 30; day++) {
        const futureDay = lastDay + day;
        const prediction = regressionLine(futureDay);
        predictedInflow += Math.max(0, prediction);
      }

      return Math.max(0, predictedInflow);
    } catch (error) {
      console.error("Error predicting supply flow:", error);
      return 0;
    }
  }

  /**
   * Predict demand outflow for the next 30 days
   * Used by inventory management for smart ordering
   */
  async predictDemandFlow(): Promise<number> {
    try {
      const productionLogs = await prisma.productionLog.findMany({
        select: {
          date: true,
          quantity: true,
        },
        orderBy: {
          date: "asc",
        },
      });

      if (productionLogs.length < 2) return 0;

      const firstDate = productionLogs[0].date.getTime();
      const dataPoints = productionLogs.map((log) => {
        const daysSinceStart = Math.floor(
          (log.date.getTime() - firstDate) / (1000 * 60 * 60 * 24)
        );
        return [daysSinceStart, log.quantity];
      });

      const regressionLine = linearRegressionLine(linearRegression(dataPoints));
      const lastDay = dataPoints[dataPoints.length - 1][0];

      let predictedOutflow = 0;
      for (let day = 1; day <= 30; day++) {
        const futureDay = lastDay + day;
        const prediction = regressionLine(futureDay);
        predictedOutflow += Math.max(0, prediction);
      }

      return Math.max(0, predictedOutflow);
    } catch (error) {
      console.error("Error predicting demand flow:", error);
      return 0;
    }
  }
}
