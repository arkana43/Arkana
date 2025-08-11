# 4K ARPG Web Demo (Genshin-like Starter)

A lightweight Babylon.js starter targeting high-quality (4K) rendering with a third-person camera, basic character movement, and post-processing. Intended as a foundation for a Genshin Impact-style action RPG prototype, including quality presets for Max/Balanced/Performance.

## Features
- Third-person follow camera with pointer-lock mouse look
- Basic WASD movement and dash
- PBR environment, shadow casting, HDR + bloom + sharpening
- Quality presets to target different GPUs (including 4K)
- Zero build tooling (CDN + static files)

## Run
- Option 1: Open `index.html` directly in a modern desktop browser (Chrome/Edge/Firefox). Some browsers restrict file URLs; prefer running a local server.
- Option 2: Serve locally:

```bash
# From this folder
python3 -m http.server 5173
# Then open http://localhost:5173 in your browser
```

## Controls
- W/A/S/D: Move
- Mouse: Look (click canvas to lock pointer)
- Space: Dash

## Notes
- Placeholder character model is `CesiumMan` from the Khronos glTF sample models.
- For a visually closer look to Genshin, replace assets with anime-styled characters, terrain, toon shading, and specialized post FX.
- For true cloud gaming, deploy the app on GPU-enabled servers and use WebRTC/streaming with authoritative server simulation. This starter is client-side only.

## Next Steps
- Implement character controller with proper acceleration, jump, and combo attacks
- Add camera collision, lock-on targeting, and aim assist
- Import world/terrain, vegetation, and sky with time-of-day system
- Add toon/outline shader pipeline and color grading
- Networked multiplayer & authoritative server (WebRTC/Colyseus/Node)