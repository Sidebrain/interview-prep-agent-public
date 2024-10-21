"use client";

import inputReducer from "@/reducers/inputReducer";
import { createContext, ReactNode, useReducer } from "react";

type InputContextType = {
  state: string;
  dispatch: React.Dispatch<{ type: string; payload: string }>;
};

const InputContext = createContext<InputContextType>({
  state: "",
  dispatch: () => {},
});

export const InputProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(inputReducer, "");
  return (
    <InputContext.Provider value={{ state, dispatch }}>
      {children}
    </InputContext.Provider>
  );
};

export default InputContext;
