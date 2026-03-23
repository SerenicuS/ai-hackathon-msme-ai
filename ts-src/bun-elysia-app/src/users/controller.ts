import { Elysia } from "elysia";
import { userService } from "./service";
import { userModel } from "./model";

const service = new userService();

export const userRoutes = new Elysia({ prefix: "users", tags: ["Users"] })
  // Existing route
  .get("/", () => "This is Users Route", {
    detail: {
      description: "Get All Users (Pagenated)",
    },
  })

  // New dynamic route with validation
  .get("/:name", ({ params }) => service.greetUser(params), {
    params: userModel.getUserParams,
    detail: {
      description: "Returns the params and says hello",
    },
  });
