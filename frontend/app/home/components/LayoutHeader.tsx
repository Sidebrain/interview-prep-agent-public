import { Icons } from "@/components/icons";
import { ModeToggle } from "@/components/ThemeSwitcher";
import { Button } from "@/components/ui/button";

type LayoutHeaderProps = {
  isLoading: boolean;
  handleSignOut: () => void;
};

export default function LayoutHeader(props: LayoutHeaderProps) {
  return (
    <header className="bg-gray-200 w-full">
      <div className="flex gap-2 p-2 w-full justify-end items-center">
        {/* <ModeToggle /> */}
        {/* <Button variant="outline">Account</Button>
        <Button variant="outline">Dashboard</Button> */}
        <Button
          variant="default"
          onClick={props.handleSignOut}
          disabled={props.isLoading}
        >
          {props.isLoading ? (
            <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            "Sign Out"
          )}
        </Button>
      </div>
    </header>
  );
}
