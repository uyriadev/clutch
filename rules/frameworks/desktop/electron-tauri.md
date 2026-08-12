# Desktop - Electron & Tauri

## Electron - the security model IS the architecture

1. **The renderer is a browser tab, not a trusted app:** `nodeIntegration: false`, `contextIsolation: true`, `sandbox: true` - these defaults stay on. Any renderer with Node access that ever touches remote content is remote code execution.
2. **All privileged operations live in the main process, exposed via a preload script + `contextBridge`** with a narrow, purpose-built API (`window.api.saveFile(data)`) - never expose `ipcRenderer` itself, `require`, or generic "run this" channels.
3. **IPC is a trust boundary:** validate sender (`senderFrame` checks for sensitive channels) and arguments in every `ipcMain.handle` - a compromised renderer will call your handlers with hostile input. Prefer `invoke`/`handle` (request-response) over `send`/`on` spaghetti.
4. **Navigation is locked down:** `will-navigate`/`setWindowOpenHandler` deny-by-default (external links via `shell.openExternal` after allowlisting the protocol), CSP on every window, no loading remote content in privileged windows, `webSecurity` never disabled.
5. **Main process stays responsive:** it runs the UI event loop coordination - heavy work goes to worker threads, `utilityProcess`, or the renderer; synchronous IPC (`sendSync`) is banned.
6. **Ship responsibly:** context-aware auto-update (electron-updater or platform stores) with signed builds - unsigned/unverified update channels are supply-chain attacks on your users; keep Electron current (each version bump is Chromium security patches).

## Tauri - capabilities over trust

7. **The frontend is untrusted here too:** privileged work lives in Rust commands (`#[tauri::command]`); expose the minimum. Rust rules apply to the backend (see rust.md) - no `unwrap` on command paths, errors mapped to serializable results.
8. **Configure the permission system tightly** (v2 capabilities/permissions; v1 allowlist): only the plugins/APIs/scopes actually used - fs scope to specific directories, shell open allowlisted, no wildcard `**` file access. The config file is a security review artifact.
9. **Commands validate their arguments** - same hostile-input assumption as Electron IPC. State via `tauri::State` with proper synchronization; long work async with progress events, never blocking a command thread.
10. **Check the Tauri major (1 vs 2)** - config schema, plugin system, and mobile support differ substantially; verify against the installed version.

## Both

11. **Follow platform conventions per OS:** menu placement (macOS app menu), keyboard shortcuts (Cmd vs Ctrl), window behavior on close (macOS hides, Windows quits - decide explicitly), file paths via the framework's path API - never hardcoded separators or home-dir guesses.
12. **Persist state in the platform's app-data location** (framework path APIs), secrets in the OS keychain (keytar-successors / tauri keyring plugins), never plaintext files or localStorage for tokens.
13. **Test the built artifact, not just dev mode:** packaging (code signing, notarization on macOS), auto-launch, deep links, and updates behave differently packaged - verify on each target OS before calling it done.
