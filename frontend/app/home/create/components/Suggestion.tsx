import { Button } from "@/components/ui/button";
import InputContext from "@/context/InputContext";
import { CheckCircleIcon } from "lucide-react";
import { useContext, useRef } from "react";

type SuggestionProps = {
  suggestion: string;
  key: number;
};

const Suggestion = ({ suggestion, key }: SuggestionProps) => {
  const { dispatch: dispatchInputValue } = useContext(InputContext);
  const suggestionRef = useRef<HTMLParagraphElement>(null);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    dispatchInputValue({
      type: "SET_INPUT",
      payload: suggestionRef.current?.textContent ?? "",
    });
  };
  const renderSuggestion = (suggestion: string) => {
    return (
      <div
        className="p-1 rounded-sm text-sm flex flex-col gap-2 items-start relative bg-transparent"
        key={key}
      >
        <p className="border p-1 bg-yellow-600 text-sm rounded-sm text-white z-10">
          Suggestion
        </p>
        <p ref={suggestionRef} className="text-sm bg-yellow-200 p-2 rounded-md">
          {suggestion}
        </p>
        <div className="flex w-full justify-end absolute bottom-0 right-0">
          <Button
            onClick={handleClick}
            variant={"outline"}
            size={"sm"}
            className="p-1"
          >
            <CheckCircleIcon className="w-4 h-4" />
          </Button>
        </div>
      </div>
    );
  };
  return <>{renderSuggestion(suggestion)}</>;
};

export default Suggestion;
