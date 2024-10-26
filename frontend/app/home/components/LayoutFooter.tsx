import Link from "next/link";

export default function LayoutFooter() {
  return (
    <footer className="bg-gray-200 w-full">
      <div className="flex gap-2 p-2 w-full text-sm justify-between">
        <Link href="/about" className="">
          About
        </Link>
        <Link href="/about">T&C</Link>
      </div>
    </footer>
  );
}
