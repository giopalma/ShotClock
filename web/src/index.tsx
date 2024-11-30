import { LocationProvider, Router, Route, hydrate, prerender as ssr } from 'preact-iso';
import { Timer } from './pages/Timer/index.js';
import { NotFound } from './pages/_404.jsx';
import './style.css';
import { Admin } from './pages/Admin/index.js';

export function App() {
	return (
		<LocationProvider>
			<Router>
				<Route path="/" component={Timer} />
				<Route path="/admin" component={Admin} />
				<Route default component={NotFound} />
			</Router>
		</LocationProvider>
	);
}

if (typeof window !== 'undefined') {
	hydrate(<App />, document.getElementById('app'));
}

export async function prerender(data) {
	return await ssr(<App {...data} />);
}
