import { WebSocketHookOptions } from "@/types/websocketTypes";
import { MessageValidator } from "../websocketMessageValidator";

export interface WebSocketCoreOptions<TState, TAction, T>
  extends WebSocketHookOptions {
  reducer: (state: TState, action: TAction) => TState;
  initialState: TState;
  validator: MessageValidator<T>;
}
