import { MessageReduceAction, WebSocketMessage } from "@/types/websocketTypes";

function messageReducer(
  state: WebSocketMessage[],
  action: MessageReduceAction
): WebSocketMessage[] {
  switch (action.type) {
    case "ADD_CHUNK":
    case "COMPLETE": {
      const messageIndex = state.findIndex(
        (msg) => msg.id === action.payload.id
      );
      if (messageIndex !== -1) {
        // message with the same id exists
        const updatedMessage = {
          ...state[messageIndex],
          content:
            (state[messageIndex].content || "") +
            (action.payload.content || ""),
          type:
            action.type === "ADD_CHUNK"
              ? ("chunk" as const)
              : ("complete" as const),
        };
        return [
          ...state.slice(0, messageIndex),
          updatedMessage,
          ...state.slice(messageIndex + 1),
        ];
      } else {
        return [...state, action.payload];
      }
    }
    case "ADD_MESSAGE":
      return [...state, action.payload];
    default:
      return state;
  }
}

export default messageReducer;
