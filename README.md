# 3D Hindi Comedy-Suspense Animation

This project renders a 3D village comedy short with Blender and adds natural Hindi character voices using the ElevenLabs Text-to-Speech API.

## GitHub Actions setup (one time)

In the repository, open **Settings → Secrets and variables → Actions → New repository secret** and add:

- `ELEVENLABS_API_KEY`: your ElevenLabs API key
- `BABLU_VOICE_ID`: voice ID selected for Bablu
- `PAPPU_VOICE_ID`: voice ID selected for Pappu
- `SARPANCH_VOICE_ID`: voice ID selected for Sarpanch
- `NARRATOR_VOICE_ID`: voice ID selected for the narrator

Keep these values private. Never paste API keys into source files, issues, or chat messages.

## Render

1. Open the **Actions** tab.
2. Select **Render 3D Animation**.
3. Tap **Run workflow** → **Run workflow**.
4. Wait for the workflow to finish.
5. Download the artifact named **bablu-pappu-mp4-with-voice**.

The voice lines and their approximate start times are in `voice_script.json`. Edit that file to change dialogue. The voice generator uses the `eleven_multilingual_v2` model and requires a valid ElevenLabs API key and four voice IDs.

## Important

- This workflow currently adds voice to the existing 32-second render. It does not yet create brand-new AI stories, generate new 3D scenes automatically, or publish to YouTube.
- The existing Blender scene is 854×480 landscape, not yet 9:16 Shorts format.
- GitHub Actions stores the MP4 as a downloadable artifact; it does not automatically upload it to YouTube.
