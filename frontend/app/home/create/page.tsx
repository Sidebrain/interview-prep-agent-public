import ChatInterface from "@/components/AiGeneratedSection/ChatInterface";
import UserGeneratedSection from "@/components/UserGeneratedSection/UserGeneratedSection";
import React from "react";

const CreateInterviewPage = () => {
  return (
    <div className="w-full flex ">
      {/* <div className="flex flex-col w-full  md:w-1/2 ">
        <UserGeneratedSection />
      </div> */}
      <div className="hidden md:flex flex-col w-2/3 m-1 items-center justify-center">
        <ChatInterface />
      </div>
    </div>
  );
};

export default CreateInterviewPage;
