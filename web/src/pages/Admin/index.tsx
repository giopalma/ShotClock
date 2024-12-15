import { ErrorAlert } from "@/components/ErrorAlert";
import GameComponent from "@/components/GameComponent";
import { Header } from "@/components/Header";
import { PresetSelect } from "@/components/PresetSelect";
import { useEffect, useState } from "preact/hooks";

export function Admin() {
	const [loading, setLoading] = useState(true);
	const [game, setGame] = useState(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const fetchData = async () => {
			try {
				const response = await fetch("/api/game");
				if (!response.ok) {
					throw new Error(response.statusText);
				}
				const result = await response.json();
				setGame(JSON.parse(result));
			} catch (err) {
				setError(err.message);
				console.log(err.message);
			} finally {
				setLoading(false);
			}
		};
		fetchData();
	}, []);

	console.log(game);

	const startNewGame = () => {
		// TODO: Richiedere all'API di iniziare un nuovo gioco
	};

	if (loading) {
		return <p>Loading...</p>;
	}

	return (
		<div>
			<Header />
			<div className="relative">
				<div className="absolute top-0 left-0 right-0 z-10 flex justify-center pt-4">
					<ErrorAlert error={error} className="max-w-80" />
				</div>
			</div>
			<div class="grid grid-rows-2 grid-cols-2 gap-4">
				<img
					src="/api/video"
					alt="device video streaming"
					className="col-span-1 row-span-2 border-2 rounded-lg p-5 w-full"
				/>
				<div class="border rounded-lg">
					<PresetSelect />
				</div>
				<div class="border rounded-lg">
					<GameComponent />
				</div>
			</div>
		</div>
	);
}
