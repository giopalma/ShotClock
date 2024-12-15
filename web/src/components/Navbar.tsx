import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

type Link = {
	name: string;
	link: string;
};
export default function Navbar({ links }: { links: Link[] }) {
	const _links = links.map((url, index) => (
		<a
			key={`url-${url.name.toLowerCase}`}
			href={url.link}
			className="flex w-full items-center py-2 text-lg font-semibold"
		>
			{url.name}
		</a>
	));
	const _links2 = links.map((url, index) => (
		<a
			key={`url2-${url.name.toLowerCase}`}
			href={url.link}
			className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-white px-4 py-2 text-sm font-medium transition-colors hover:bg-gray-100 hover:text-gray-900 focus:bg-gray-100 focus:text-gray-900 focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-gray-100/50 data-[state=open]:bg-gray-100/50 dark:bg-gray-950 dark:hover:bg-gray-800 dark:hover:text-gray-50 dark:focus:bg-gray-800 dark:focus:text-gray-50 dark:data-[active]:bg-gray-800/50 dark:data-[state=open]:bg-gray-800/50"
		>
			{url.name}
		</a>
	));
	const project_name = "Shot Clock"; //TODO: Forse usare una variabile d'ambiente sarebbe il caso
	return (
		<header className="flex h-20 w-full shrink-0 items-center px-4 md:px-6">
			<Sheet>
				<SheetTrigger asChild>
					<Button variant="outline" size="icon" className="lg:hidden">
						<MenuIcon className="h-6 w-6" />
						<span className="sr-only">Toggle navigation menu</span>
					</Button>
				</SheetTrigger>
				<SheetContent side="left">
					<a href="/" className="mr-6 hidden lg:flex">
						<UniudIcon className="h-6 w-6" />
						<span className="sr-only">{project_name}</span>
					</a>
					<div className="grid gap-2 py-6">{_links}</div>
				</SheetContent>
			</Sheet>
			<a href="/" className="mr-6 hidden lg:flex">
				<UniudIcon className="h-12 w-12" />
				<span className="sr-only">{project_name}</span>
			</a>
			<nav className="ml-auto hidden lg:flex gap-6">{_links2}</nav>
		</header>
	);
}

function MenuIcon(props) {
	return (
		<svg
			{...props}
			xmlns="http://www.w3.org/2000/svg"
			width="24"
			height="24"
			viewBox="0 0 24 24"
			fill="none"
			stroke="currentColor"
			strokeWidth="2"
			strokeLinecap="round"
			strokeLinejoin="round"
		>
			<title>Menu</title>
			<line x1="4" x2="20" y1="12" y2="12" />
			<line x1="4" x2="20" y1="6" y2="6" />
			<line x1="4" x2="20" y1="18" y2="18" />
		</svg>
	);
}

function UniudIcon(props) {
	return <img {...props} src="/uniud.svg" alt="Uniud Logo" />;
}
