import { useEffect, useState } from "preact/hooks"

export function Timer() {
	const [loading, setLoading] = useState(true)
	const [game, setGame] = useState(null)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		const fetchData = async () => {
			try {
				const response = await fetch('/api/game');
				if (!response.ok) {
					throw new Error(response.statusText)
				}
				const result = await response.json()
				setGame(result)
			} catch (err) {
				setError(err.message)
				console.log(err.message)
			} finally {
				setLoading(false);
			}
		}
		fetchData()
	}, [])

	return (
		<div>
			{loading && <p>Loading...</p>}
			{error && <p>Error: {error}</p>}
			{game &&
				<div>
					<span>05:00</span>
				</div>
			}
		</div>
	);
}
