"use client";
import { Button } from "@/components/ui/button";
import { PlusCircleIcon } from "lucide-react";
import { useRouter } from "next/navigation";

const Home = () => {
  const router = useRouter();
  return (
    <div className="bg-red-200 w-full items-center justify-center flex ">
      <Button
        onClick={() => {
          router.push("home/create");
        }}
        variant="secondary"
        className="gap-2 p-8 text-lg"
      >
        <PlusCircleIcon size={36} className="m-0" />
        Create an Interviewer
      </Button>
    </div>
  );
};

export default Home;
