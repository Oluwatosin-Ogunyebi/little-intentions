# Credits

- Orbit source artwork: the owner's custom ChatGPT pet, supplied in `assets/orbit/source/`; original artwork and metadata were preserved. The in-game 3D interpretation was authored in Blender for this project by the explicitly requested GPT-6 Astra subagent, with Terra review and integration.
- Application, simulation, interface, and verification: Codex coding session led by Terra. See `CODEX_LOG.md` for the actual work and checks.
- Three.js, Vite, TypeScript, Express, Playwright, and other npm dependencies: see `package-lock.json` and each dependency's licence. Blender was used for asset authoring.
- DM Sans and DM Serif Display are requested from Google Fonts when available; the interface has system font fallbacks. Review font licensing and hosting before publishing.
- The owner tested Quest placement and reported it comfortable. No formal user study, measured learning outcome, or Quest performance benchmark is claimed; the live checks are limited observations recorded in the build log.
- Runtime API services: OpenAI Responses (`gpt-6-luna`), transcription (`gpt-transcribe`) and generated speech (`gpt-4o-mini-tts`, `coral`); speech model deprecation is noted in the capability status. Victory and ambience sounds are synthesized in the browser, and confetti is rendered with Three.js.
