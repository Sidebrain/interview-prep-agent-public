type OptionProps = {
  option: string;
};

const Option = ({ option}: OptionProps) => {
  return (
    <div
      className="p-1 rounded-sm text-sm flex flex-col gap-2 items-start relative bg-transparent"
    >
      <p className="border p-1 bg-yellow-600 text-sm rounded-sm text-white z-10">
        Options
      </p>
      <p className="text-sm bg-yellow-200 p-2 rounded-md">
        {option}
      </p>
    </div>
  );
};

export default Option;
