import { useArtifact } from "@/context/ArtefactContext";
import ArtefactFrame from "./ArtefactFrame";

const GenerativeArea = () => {
  const { artifactText } = useArtifact();
  if (!artifactText) return null;
  return (
    <div
      className={`bg-gray-100 h-full flex flex-col items-center p-4 ${
        artifactText ? "w-full md:w-1/2" : "hidden"
      }`}
    >
      <ArtefactFrame />
    </div>
  );
};

export default GenerativeArea;
