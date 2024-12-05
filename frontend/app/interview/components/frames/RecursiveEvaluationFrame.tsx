// Type definitions
type RecursiveData =
  | string
  | number
  | boolean
  | null
  | RecursiveData[]
  | { [key: string]: RecursiveData };

interface RecursiveEvaluationFrameProps {
  data: RecursiveData;
  depth?: number;
}

// Helper functions
const renderArray = (data: RecursiveData[], depth: number) => {
  return (
    <ul className="list-disc ml-4">
      {data.map((item, index) => (
        <li key={index}>
          {typeof item === "object" ? (
            <RecursiveEvaluationFrame data={item} depth={depth + 1} />
          ) : (
            <div>{item}</div>
          )}
        </li>
      ))}
    </ul>
  );
};

const renderObject = (
  data: Record<string, RecursiveData>,
  depth: number
) => {
  return (
    <div className={`${depth > 0 ? "ml-4" : ""}`}>
      {Object.entries(data).map(([key, value]) => (
        <div key={key} className="mb-2">
          <div className="font-semibold text-gray-700">
            {key.replace(/_/g, " ").toUpperCase()}:
          </div>
          <div className="ml-2">
            {typeof value === "object" && value !== null ? (
              <RecursiveEvaluationFrame
                data={value}
                depth={depth + 1}
              />
            ) : (
              String(value)
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

// Main component
const RecursiveEvaluationFrame: React.FC<
  RecursiveEvaluationFrameProps
> = ({ data, depth = 0 }) => {
  if (Array.isArray(data)) {
    return renderArray(data, depth);
  }

  if (typeof data === "object" && data !== null) {
    return renderObject(data, depth);
  }

  return <span>{String(data)}</span>;
};

export default RecursiveEvaluationFrame;
