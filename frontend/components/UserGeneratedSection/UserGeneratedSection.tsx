import FormInputs from "./FormInputs";

type Props = {};

const UserGeneratedSection = (props: Props) => {
  return (
    <div className="flex flex-col w-full  md:w-1/2 ">
      <div id="container" className="flex flex-col m-8 px-16">
        <FormInputs />
      </div>
    </div>
  );
};

export default UserGeneratedSection;
