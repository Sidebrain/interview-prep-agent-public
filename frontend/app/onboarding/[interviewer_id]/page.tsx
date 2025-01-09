import { Interviewer } from "@/app/onboarding/types";
import { WebsocketFrame } from "@/types/ScalableWebsocketTypes";

export const MemoryFrames = ({ frame }: { frame: WebsocketFrame }) => {
  return (
    <div className="space-y-2">
        <div key={frame.frameId} className="bg-gray-100 p-2 rounded">
          <div><strong>Frame ID:</strong> {frame.frameId}</div>
          <div><strong>Type:</strong> {frame.type}</div>
          <div><strong>Address:</strong> {frame.address || 'N/A'}</div>
          <div className="mt-2">
            <strong>Content:</strong>
            <pre className="whitespace-pre-wrap mt-1">
              {frame.frame.content || frame.frame.delta || 'N/A'}
            </pre>
          </div>
        </div>
    </div>
  );
};

const verifyInterviewerId = async (interviewer_id: string): Promise<Interviewer | null> => {
  // verify the interviewer_id is valid
  // if valid then return true
  // if not valid then return false
  const response = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/api/v3/interview/' + interviewer_id, {
    method: 'GET',
  });
  if (!response.ok) {
    return null;
  }
  const data = await response.json();
  console.log(data);
  return data;
};

const EntryPage = async ({ params }: { params: { interviewer_id: string } }) => {
  let slug = params.interviewer_id;
  if (slug === 'test') {
    slug = '37c08382-0557-4fd2-b4ba-f04bccd30eed';
  }
  const interviewer = await verifyInterviewerId(slug);
  // steps
  // first verify that the interviewer_id is valid
  // if valid then launch the onboarding flow to register the candidate 
  // if not valid then error 404 page
  if (!interviewer) {
    return <div>Invalid interviewer_id</div>;
  }
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Interviewer Details</h1>
      <div className="space-y-4">
        <div className="flex flex-col gap-2">
          <h2 className="font-semibold">ID:</h2>
          <pre className="bg-gray-100 p-2 rounded">{interviewer._id}</pre>
        </div>
        <div>
          <h2 className="font-semibold">Created At:</h2>
          <pre className="bg-gray-100 p-2 rounded">
            {new Date(interviewer.created_at).toLocaleString()}
          </pre>
        </div>
        <div>
          <h2 className="font-semibold">Updated At:</h2>
          <pre className="bg-gray-100 p-2 rounded">
            {new Date(interviewer.updated_at).toLocaleString()}
          </pre>
        </div>
        <div>
          <h2 className="font-semibold">Job Description:</h2>
          <pre className="bg-gray-100 p-2 rounded whitespace-pre-wrap">
            {interviewer.job_description}
          </pre>
        </div>
        <div>
          <h2 className="font-semibold">Rating Rubric:</h2>
          <pre className="bg-gray-100 p-2 rounded whitespace-pre-wrap">
            {interviewer.rating_rubric}
          </pre>
        </div>
        <div>
          <h2 className="font-semibold">Question Bank:</h2>
          <pre className="bg-gray-100 p-2 rounded whitespace-pre-wrap">
            {interviewer.question_bank}
          </pre>
        </div>
        <div className="flex flex-col gap-4">
          <h2 className="font-semibold">Memory ({interviewer.memory.length} frames):</h2>
          {interviewer.memory.map((frame) => (
            <MemoryFrames key={frame.frameId} frame={frame} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default EntryPage;