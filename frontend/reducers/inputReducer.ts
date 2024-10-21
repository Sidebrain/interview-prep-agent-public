const inputReducer = (
  state: string,
  action: { type: string; payload: string }
) => {
  switch (action.type) {
    case "SET_INPUT":
      return action.payload;
    case "APPEND_INPUT":
      return state + "\n" + action.payload;
    default:
      return state;
  }
};

export default inputReducer;
