import ChatInterface from "@/components/AiGeneratedSection/ChatInterface";
import SimpleChatInterface from "@/components/AiGeneratedSection/SimpleChatInterface";
import UserGeneratedSection from "@/components/UserGeneratedSection/UserGeneratedSection";
import React from "react";

const CreateInterviewPage = () => {
  return (
    <div className="w-full flex ">
      <UserGeneratedSection />
      <div className="hidden md:flex flex-col w-1/2 m-1 items-center justify-center">
        {/* <ChatInterface /> */}
        <SimpleChatInterface />
      </div>
    </div>
  );
};

export default CreateInterviewPage;
