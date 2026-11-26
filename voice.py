import json
import os
import pathlib
import subprocess
import tempfile
import requests

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
VIDEO = OUT / "bablu_pappu_well.mp4"
VOICE_TRACK = OUT / "voice_mix.mp3"
FINAL = OUT / "bablu_pappu_with_voice.mp4"

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_IDS = {
    "bablu": os.environ.get("BABLU_VOICE_ID"),
    "pappu": os.environ.get("PAPPU_VOICE_ID"),
    "sarpanch": os.environ.get("SARPANCH_VOICE_ID"),
    "narrator": os.environ.get("NARRATOR_VOICE_ID"),
}
if not API_KEY:
    raise SystemExit("Missing ELEVENLABS_API_KEY GitHub Actions secret.")
if not VIDEO.exists():
    raise SystemExit(f"Video not found: {VIDEO}")

script = json.loads((ROOT / "voice_script.json").read_text(encoding="utf-8"))
headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
temp_files = []
filters = []
inputs = []

with tempfile.TemporaryDirectory() as temp_dir:
    for i, line in enumerate(script["lines"]):
        role = line["role"].lower()
        voice_id = VOICE_IDS.get(role)
        if not voice_id:
            raise SystemExit(f"Missing GitHub secret for {role.upper()}_VOICE_ID")
        payload = {
            "text": line["text"],
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.58,
                "similarity_boost": 0.78,
                "style": 0.12,
                "use_speaker_boost": True
            }
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        response = requests.post(
            url, headers=headers, json=payload,
            params={"output_format": "mp3_44100_128"}, timeout=120
        )
        if response.status_code != 200:
            raise SystemExit(
                f"ElevenLabs failed for line {i+1}: "
                f"{response.status_code} {response.text[:500]}"
            )
        audio_path = pathlib.Path(temp_dir) / f"line_{i:02d}.mp3"
        audio_path.write_bytes(response.content)
        inputs.extend(["-i", str(audio_path)])
        delay_ms = int(float(line["start"]) * 1000)
        filters.append(
            f"[{i}:a]adelay={delay_ms}|{delay_ms},"
            f"apad=pad_dur=32[a{i}]"
        )

    mix_inputs = "".join(f"[a{i}]" for i in range(len(script["lines"])))
    filter_complex = ";".join(filters) + ";" + mix_inputs + (
        f"amix=inputs={len(script['lines'])}:duration=longest:normalize=0,"
        "atrim=0:32, loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y", *inputs, "-filter_complex", filter_complex,
        "-map", "[aout]", "-codec:a", "libmp3lame", "-b:a", "192k",
        str(VOICE_TRACK)
    ], check=True)

subprocess.run([
    "ffmpeg", "-y", "-i", str(VIDEO), "-i", str(VOICE_TRACK),
    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-shortest", str(FINAL)
], check=True)
print(f"Created voiced video: {FINAL}")
