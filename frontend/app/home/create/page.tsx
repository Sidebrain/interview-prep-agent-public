import { InputProvider } from "@/context/InputContext";
import UserArea from "./components/UserArea";

export default function InteractionArea() {
  // hooks here

  return (
    <div className="w-full p-2">
      <InputProvider>
        <UserArea />
      </InputProvider>
    </div>
  );
}
