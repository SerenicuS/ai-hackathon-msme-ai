// Forecasting module - Elysia schemas and validation models

import { t, Static } from "elysia";

// Response schema for predict-demand endpoint
export const forecastingModel = {
  predictDemandResponse: t.Object({
    status: t.String(),
    message: t.String(),
    forecast_total_kg: t.Optional(t.Number()),
  }),

  errorResponse: t.Object({
    status: t.String(),
    message: t.String(),
  }),
};

// Extract TypeScript types
export type PredictDemandResponse = Static<
  typeof forecastingModel.predictDemandResponse
>;
export type ErrorResponse = Static<typeof forecastingModel.errorResponse>;
