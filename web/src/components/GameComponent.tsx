import { useState } from "react";
import { Button } from "@/components/ui/button";

interface Game {
	turn_duration: number;
	player1_name: string;
	player2_name: string;
	current_player: number;
	timers: {
		1: number | null;
		2: number | null;
	};
	status: "ready" | "playing" | "paused";
}

export default function GameComponent() {
	const [game, setGame] = useState<Game | null>(null);

	const startNewGame = () => {
		setGame({
			turn_duration: 30,
			player1_name: "Giovanni",
			player2_name: "Paolo",
			current_player: 1,
			timers: {
				1: null,
				2: null,
			},
			status: "ready",
		});
	};

	const handleStart = () => {
		if (game) {
			setGame({ ...game, status: "playing" });
			// Avvia i timer qui se necessario
		}
	};

	const handleStop = () => {
		if (game) {
			setGame({ ...game, status: "paused" });
			// Ferma i timer qui se necessario
		}
	};

	const formattedTime = (seconds: number) => {
		const minutes = Math.floor(seconds / 60);
		const remainingSeconds = seconds % 60;
		return `${minutes.toString().padStart(2, "0")}:${remainingSeconds
			.toString()
			.padStart(2, "0")}`;
	};

	return (
		<div class="w-full h-full">
			{game === null ? (
				<div className="text-center space-y-4">
					<p className="text-lg font-medium">Nessun gioco in corso</p>
					<Button onClick={startNewGame}>Inizia un nuovo gioco</Button>
				</div>
			) : (
				<>
					<div className="text-center">
						<p className="text-lg font-medium">Giocatori</p>
						<div className="flex justify-center space-x-4 mt-2">
							<div
								className={`p-2 rounded-md ${
									game.current_player === 1 ? "bg-blue-100" : ""
								}`}
							>
								<p className="font-semibold">{game.player1_name}</p>
							</div>
							<div
								className={`p-2 rounded-md ${
									game.current_player === 2 ? "bg-blue-100" : ""
								}`}
							>
								<p className="font-semibold">{game.player2_name}</p>
							</div>
						</div>
					</div>
					<div className="text-center">
						<p className="text-lg font-medium">Tempo del turno</p>
						<p className="text-2xl font-bold">
							{formattedTime(game.turn_duration)}
						</p>
					</div>
					<div className="flex justify-center space-x-4">
						<Button onClick={handleStart} disabled={game.status === "playing"}>
							Start
						</Button>
						<Button
							onClick={handleStop}
							variant="secondary"
							disabled={game.status !== "playing"}
						>
							Stop
						</Button>
					</div>
				</>
			)}
		</div>
	);
}
