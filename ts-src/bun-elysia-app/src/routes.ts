import { Elysia } from "elysia";
import { userRoutes } from "./users/controller";
import { supplierRoutes } from "./suppliers/controller";
import { forecastingRoutes } from "./forecasting/controller";
import { inventoryRoutes } from "./inventory/controller";

export const apiRoutes = new Elysia()
  .use(supplierRoutes)
  .use(forecastingRoutes)
  .use(inventoryRoutes)
  .use(userRoutes); // Keep existing example route
