// Suppliers module - Elysia schemas and validation models

import { t, Static } from "elysia";

// Response schema for update-scores endpoint
export const supplierModel = {
  updateScoresResponse: t.Object({
    status: t.String(),
    message: t.String(),
    data: t.Optional(
      t.Array(
        t.Object({
          supplier_id: t.String(),
          name: t.String(),
          location: t.Any(), // JSON object
          reliability_score: t.Number(),
          description: t.Any(), // JSON object
          eligibility: t.Any(), // JSON object
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
export type UpdateScoresResponse = Static<
  typeof supplierModel.updateScoresResponse
>;
export type ErrorResponse = Static<typeof supplierModel.errorResponse>;
