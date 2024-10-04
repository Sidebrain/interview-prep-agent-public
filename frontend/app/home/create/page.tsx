import UserGeneratedSection from "@/components/UserGeneratedSection/UserGeneratedSection";
import React from "react";

const CreateInterviewPage = () => {
  return (
    <div className="w-full flex ">
      <UserGeneratedSection />
      <div className="hidden md:flex flex-col w-1/2 bg-gray-300 m-1 items-center justify-center">
        Generative Area
      </div>
    </div>
  );
};

export default CreateInterviewPage;
