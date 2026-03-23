import { GetUserResponse, GetUserParams } from "./model";

export class userService {
  greetUser(params: GetUserParams): GetUserResponse {
    return {
      name: params.name,
      message: `Hello, ${params.name}`,
    };
  }
}
