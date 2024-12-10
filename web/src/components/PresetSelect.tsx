import { useEffect, useState } from "preact/hooks";
import {
	Select,
	SelectTrigger,
	SelectValue,
	SelectItem,
	SelectContent,
} from "./ui/select";
import { Label } from "./ui/label";

export function PresetSelect() {
	const [tables, setTables] = useState([]);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const fetchData = async () => {
			try {
				const response = await fetch("/api/table");
				if (!response.ok) {
					throw new Error(response.statusText);
				}
				const result = await response.json();
				setTables(result);
			} catch (err) {
				setError(err.message);
				console.log(err.message);
			} finally {
			}
		};
		fetchData();
	}, []);

	//if (error) return <span>Error: {error}</span>;

	const selectItems = tables.map((table) => (
		<SelectItem key={table.id} value={table.id}>
			{table.name}
		</SelectItem>
	));

	return (
		<>
			<Label>Preset del tavolo</Label>
			<Select>
				<SelectTrigger className="w-[180px]">
					<SelectValue placeholder="" />
				</SelectTrigger>
				<SelectContent>{selectItems}</SelectContent>
			</Select>
		</>
	);
}
