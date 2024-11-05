export default function Debug() {
  return (
    <div className="flex flex-col">
      <h1>Environment Variables</h1>
      <pre className="flex flex-col gap-2">
        <p className="bg-gray-200 p-2">
          NEXT_PUBLIC_WS_URL: {process.env.NEXT_PUBLIC_WS_URL}
        </p>
        <p className="bg-gray-200 p-2">
          NEXT_PUBLIC_WS_URL_V2: {process.env.NEXT_PUBLIC_WS_URL_V2}
        </p>
      </pre>
    </div>
  );
}
