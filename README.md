# 3D Hindi Comedy-Suspense Animation

This project creates a short 3D animated Hindi comedy-suspense video using Blender.

## What it creates
- A stylized night-time village scene with a haunted well
- Two cartoon-style friends, Bablu and Pappu
- Camera moves, lighting, subtitles and a suspense-comedy ending
- MP4 output at `output/bablu_pappu_well.mp4`

## Render on GitHub
1. Open the **Actions** tab.
2. Select **Render 3D Animation**.
3. Tap **Run workflow** → **Run workflow**.
4. Wait for the workflow to finish.
5. Open the completed run and download the artifact named **bablu-pappu-mp4**.

The first render may take several minutes. GitHub stores the rendered MP4 as a downloadable workflow artifact; it does not automatically publish it to YouTube.

## Render on a computer with Blender
Run:
```bash
blender -b --python render.py
```

The render is silent. Add voice-over and sound effects in a video editor before publishing.
