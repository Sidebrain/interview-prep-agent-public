import { useArtifact } from "@/context/ArtifactContext";
import ArtifactFrame from "./ArtifactFrame";

const GenerativeArea = () => {
  const { artifactObject, focus } = useArtifact();
  if (Object.keys(artifactObject).length === 0) return null;
  return (
    <div
      className={`bg-gray-100 h-full flex flex-col items-center p-4 ${
        focus.title ? "w-full md:w-1/2" : "hidden"
      }`}
    >
      <ArtifactFrame />
    </div>
  );
};

export default GenerativeArea;
