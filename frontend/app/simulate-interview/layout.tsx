import React from "react";
import Header from "../home/layout";

const InterviewLayout = ({ children }: { children: React.ReactNode }) => {
  return <Header>{children}</Header>;
};

export default InterviewLayout;
