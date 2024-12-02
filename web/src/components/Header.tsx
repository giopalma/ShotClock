import { useLocation } from 'preact-iso';
import Navbar from './Navbar';

export function Header() {
	//const { url } = useLocation();
	return (
		<header>
			<Navbar links={[{ name: 'Timer', link: '/' }, { name: 'Admin', link: '/admin' }]} />
		</header>
	);
}
