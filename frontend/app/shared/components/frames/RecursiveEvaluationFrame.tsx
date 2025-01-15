type RecursiveEvaluationFrameProps = {
  data: any;
  depth?: number;
};

export const RecursiveEvaluationFrame: React.FC<
  RecursiveEvaluationFrameProps
> = ({ data, depth = 0 }) => {
  // Handle if it is an array

  if (Array.isArray(data)) {
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
  }
  // Handle object case
  if (typeof data === "object" && data !== null) {
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
  }
  return <span>{String(data)}</span>;
};
