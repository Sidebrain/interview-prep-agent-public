import { useArtifact } from "@/context/ArtifactContext";
import ArtifactFrame from "./ArtifactFrame";

const GenerativeArea = () => {
  const { artifact } = useArtifact();
  if (!artifact) return null;
  return (
    <div
      className={`bg-gray-100 h-full flex flex-col items-center p-4 ${
        artifact ? "w-full md:w-1/2" : "hidden"
      }`}
    >
      <ArtifactFrame />
    </div>
  );
};

export default GenerativeArea;
