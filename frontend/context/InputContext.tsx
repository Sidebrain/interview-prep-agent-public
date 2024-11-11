"use client";

import inputReducer, { InputActionType } from "@/reducers/inputReducer";
import { createContext, ReactNode, useContext, useReducer } from "react";

type InputContextType = {
  state: string;
  dispatch: React.Dispatch<{ type: InputActionType; payload: string }>;
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

export const useInput = () => {
  const context = useContext(InputContext);
  if (context === undefined) {
    throw new Error("useInput must be used within an InputProvider");
  }
  return context;
};

export default InputContext;
