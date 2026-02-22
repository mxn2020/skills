---
name: ffmpeg-processor
id: OC-0098
version: 1.0.0
description: "FFmpeg video processing – cut, merge, transcode, watermark, and more"
env: []
commands:
  - cut
  - merge
  - transcode
  - watermark
  - extract-audio
  - resize
  - info
---

# FFmpeg Processor

Process videos locally using FFmpeg: cut, merge, transcode, add watermarks, and extract audio.

## Prerequisites
- `ffmpeg` and `ffprobe` must be installed and available in your PATH.

## Commands
| Command          | Description                                    |
|------------------|------------------------------------------------|
| `cut`            | Cut a clip from a video by time range          |
| `merge`          | Concatenate multiple videos into one           |
| `transcode`      | Re-encode a video with a different codec       |
| `watermark`      | Overlay an image watermark onto a video        |
| `extract-audio`  | Extract the audio track from a video           |
| `resize`         | Resize video to specific dimensions or scale   |
| `info`           | Display video metadata and stream information  |

## Usage
```bash
python3 scripts/ffmpeg_processor.py cut --input video.mp4 --start 00:00:10 --end 00:01:30 --output clip.mp4
python3 scripts/ffmpeg_processor.py merge --inputs clip1.mp4 clip2.mp4 clip3.mp4 --output merged.mp4
python3 scripts/ffmpeg_processor.py transcode --input video.mp4 --output output.mp4 --codec libx265 --crf 28
python3 scripts/ffmpeg_processor.py watermark --input video.mp4 --watermark logo.png --position bottom-right --output branded.mp4
python3 scripts/ffmpeg_processor.py extract-audio --input video.mp4 --output audio.mp3
python3 scripts/ffmpeg_processor.py resize --input video.mp4 --width 1280 --height 720 --output resized.mp4
python3 scripts/ffmpeg_processor.py info --input video.mp4
```
