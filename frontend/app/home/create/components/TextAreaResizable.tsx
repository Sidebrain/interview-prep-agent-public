import { Textarea } from "@/components/ui/textarea";
import InputContext from "@/context/InputContext";
import { forwardRef, useContext, useEffect } from "react";

type TextAreaProps = {
  maxTextareaHeight: number;
  handleSubmit: (e: React.FormEvent) => void;
};

const TextareaResizable = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  (props: TextAreaProps, ref) => {
    const { state: inputValue, dispatch: dispatchInputValue } =
      useContext(InputContext);

    function adjustTextareaHeight() {
      if (ref && typeof ref !== "function" && ref.current) {
        ref.current.style.height = "auto";
        const newHeight = Math.min(
          ref.current.scrollHeight,
          props.maxTextareaHeight
        );
        ref.current.style.height = `${newHeight}px`;
      }
    }

    function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        props.handleSubmit(e);
      }
    }

    function handleInputChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
      dispatchInputValue({
        type: "SET_INPUT",
        payload: e.target.value,
      });
      adjustTextareaHeight();
    }

    useEffect(() => {
      adjustTextareaHeight();
    }, [props.maxTextareaHeight, inputValue]);

    return (
      <Textarea
        ref={ref}
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={onKeyDown}
        className="resize-none w-full p-2 focus-visible:ring-transparent"
      />
    );
  }
);

export default TextareaResizable;
