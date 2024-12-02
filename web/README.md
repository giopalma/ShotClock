<h2 align="center">Web interface for Billiard Timer</h3>

Viene utilizzato [Preact](https://preactjs.com/) e [Vite](https://vitejs.dev/) per creare l'interfaccia web.

La comunicazione con il server avviene tramite HTTP e WebSocket ([SocketIO](https://socket.io/))

## Comandi utili

- `pnpm dev` - Starts a dev server at http://localhost:5173/

- `pnpm build` - Builds for production, emitting to `dist/`. Prerenders all found routes in app to static HTML

- `pnpm preview` - Starts a server at http://localhost:4173/ to test production build locally
