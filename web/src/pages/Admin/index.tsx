import { ErrorAlert } from "@/components/ErrorAlert"
import { Header } from "@/components/Header"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "preact/hooks"



export function Admin() {
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

    const startNewGame = () => {
        // TODO: Richiedere all'API di iniziare un nuovo gioco
    }

    if (loading) {
        return (
            <p>Loading...</p>
        )
    }

    return (
        <>
            <Header />
            <ErrorAlert error={error} />
            {game == null &&
                <>
                    <p>Nessun gioco in corso</p>
                    <Button onClick={startNewGame}>Inizia un nuovo gioco</Button>
                </>
            }
            <img src="/api/video" width="600"></img>
        </>
    )
}