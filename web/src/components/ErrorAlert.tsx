import { AlertCircle } from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

export function ErrorAlert(props) {
	if (props.error) {
		return (
			<Alert variant="destructive" {...props}>
				<AlertCircle className="h-4 w-4" />
				<AlertTitle>Errore</AlertTitle>
				<AlertDescription>{props.error}</AlertDescription>
			</Alert>
		);
	}
	return null;
}
