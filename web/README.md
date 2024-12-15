<h2 align="center">Web interface for Shot Clock</h3>

Viene utilizzato [Preact](https://preactjs.com/) e [Vite](https://vitejs.dev/) per creare l'interfaccia web.

La comunicazione con il server avviene tramite HTTP e WebSocket ([SocketIO](https://socket.io/))

Viene utilizzato [TailwindCSS](https://tailwindcss.com/) per lo stile e [shadcn/ui](https://ui.shadcn.com/) per i componenti di base.

Viene utilizzato [Biome](https://biomejs.dev/) per la formattazione del codice e il linting del codice.

## Installazione

Utilizzo il gestore di pacchetti [pnpm](https://pnpm.io) che permette di utilizzare gli stessi comandi di `npm` (basta aggiungere una `p` prima di ogni comando) ma con una gestione dei pacchetti più efficiente e veloce e riducendo notevolmente lo spazio in memoria. Di fatti a differenza di npm, pnpm non crea una cartella node_modules per ogni pacchetto installato, ma li condivide tra i progetti che li utilizzano. L'installazione di `pnpm` è semplice: https://pnpm.io/installation

- `pnpm install` - Installa le dipendenze

## Comandi utili

- `pnpm dev` - Starts a dev server at http://localhost:5173/

- `pnpm build` - Builds for production, emitting to `dist/`. Prerenders all found routes in app to static HTML

- `pnpm preview` - Starts a server at http://localhost:4173/ to test production build locally
