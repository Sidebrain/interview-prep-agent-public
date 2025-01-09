const verifyInterviewerId = async (interviewer_id: string) => {
  // verify the interviewer_id is valid
  // if valid then return true
  // if not valid then return false
  const response = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + '/api/v3/interview/' + interviewer_id, {
    method: 'GET',
  });
  if (!response.ok) {
    return false;
  }
  const data = await response.json();
  console.log(data);
  return true;
};

const EntryPage = async ({ params }: { params: { interviewer_id: string } }) => {
  let slug = params.interviewer_id;
  if (slug === 'test') {
    slug = '37c08382-0557-4fd2-b4ba-f04bccd30eed';
  }
  const isValid = await verifyInterviewerId(slug);
  // steps
  // first verify that the interviewer_id is valid
  // if valid then launch the onboarding flow to register the candidate 
  // if not valid then error 404 page
  return <div>EntryPage {slug} is {isValid ? 'valid' : 'invalid'}</div>;
};

export default EntryPage;