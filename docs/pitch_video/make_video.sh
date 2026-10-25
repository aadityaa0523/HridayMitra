#!/usr/bin/env bash
# Builds docs/demo/hridaymitra_pitch.mp4 (4:00, 1080p30): motion graphics + Wokwi demo clip + original music.
# Needs node + playwright (chromium), ffmpeg, python3 with numpy/scipy. About 10 minutes on 4 cores.
set -euo pipefail
cd "$(dirname "$0")"; W=$(mktemp -d)
for i in 0 1 2 3; do node render.js "$W/part$i.mp4" 30 $((i*60)) $((i*60+60)) & done; wait
printf "file '%s'\n" "$W"/part{0,1,2,3}.mp4 > "$W/list.txt"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$W/list.txt" -c copy "$W/silent.mp4"
python3 music.py "$W/music.wav"
# Wokwi month demo (real firmware) into the black frame of the Wokwi scene, 141.0-151.4 s
ffmpeg -y -loglevel error -i "$W/silent.mp4" -ss 14 -t 10.4 -i ../demo/hridaymitra_month_demo.mp4 -i "$W/music.wav" \
  -filter_complex "[1:v]scale=1200:675,format=yuva420p,fade=in:st=0:d=0.5:alpha=1,fade=out:st=9.8:d=0.6:alpha=1,setpts=PTS-STARTPTS+141/TB[c];[0:v][c]overlay=360:270:enable='between(t,141,151.4)':eof_action=pass[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart ../demo/hridaymitra_pitch.mp4
rm -rf "$W"; echo "done: docs/demo/hridaymitra_pitch.mp4"
