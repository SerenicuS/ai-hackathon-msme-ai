import { Elysia } from "elysia";
import { openapi } from "@elysiajs/openapi";
import { apiRoutes } from "./routes";

const app = new Elysia()
  .use(
    openapi({
      documentation: {
        info: {
          version: "v1",
          title: "Cacao MSME Management API",
          description:
            "Smart cacao supply chain management system with AI-powered supplier scoring, demand forecasting, and intelligent inventory management. Built with Bun and Elysia for fast, type-safe operations.",
        },
      },
    }),
  )
  .get("/", () => "Cacao MSME Management API - Visit /openapi for documentation", {
    detail: {
      hide: true,
    },
  })
  .group("/api/v1", (app) => app.use(apiRoutes))
  .listen(8080);

console.log(
  `🦊 Elysia is running at ${app.server?.hostname}:${app.server?.port}`,
);
