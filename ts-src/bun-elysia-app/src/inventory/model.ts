// Inventory module - Elysia schemas and validation models

import { t, Static } from "elysia";

// Response schema for suggest-orders endpoint
export const inventoryModel = {
  suggestOrdersResponse: t.Object({
    status: t.String(),
    message: t.String(),
    analysis: t.Object({
      current_storage: t.Number(),
      projected_end_stock: t.Optional(t.Number()),
      predicted_usage_spike: t.Optional(t.Number()),
      required_purchase_kg: t.Number(),
    }),
    ai_suggestion: t.Optional(
      t.Array(
        t.Object({
          supplier: t.String(),
          rank_score: t.Number(),
          suggested_order_kg: t.Number(),
          reason: t.String(),
        })
      )
    ),
  }),

  errorResponse: t.Object({
    status: t.String(),
    message: t.String(),
  }),
};

// Extract TypeScript types
export type SuggestOrdersResponse = Static<
  typeof inventoryModel.suggestOrdersResponse
>;
export type ErrorResponse = Static<typeof inventoryModel.errorResponse>;
