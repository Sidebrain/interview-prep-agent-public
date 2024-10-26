import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

export function PopoverComponent() {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size={"sm"}
          className="bg-gray-200 font-bold rounded-lg "
        >
          Model controls
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Set Parameters</h4>
            <p className="text-sm text-muted-foreground">
              Control the generation of the model
            </p>
          </div>
          <div className="grid gap-2">
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="temperature" className="text-sm">
                Temperature
              </Label>
              <Input
                type="number"
                id="temperature"
                defaultValue="1.0"
                step="0.1"
                min="0"
                max="1"
                className="col-span-2 h-8"
              />
            </div>
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="top-p" className="text-sm">
                Top P
              </Label>
              <Input
                type="number"
                id="top-p"
                defaultValue="0.9"
                step="0.1"
                min="0"
                max="1"
                className="col-span-2 h-8"
              />
            </div>
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="limit-tokens" className="text-sm">
                Limit Tokens
              </Label>
              <Input
                type="number"
                id="limit-tokens"
                defaultValue="256"
                min="1"
                className="col-span-2 h-8"
              />
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
