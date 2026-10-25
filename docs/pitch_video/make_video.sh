#!/usr/bin/env bash
# Builds hridaymitra_pitch.mp4 (1080p30, about 3:46): story + chair demo motion graphics, offline neural voice-over,
# original music ducked under the voice, and the Wokwi firmware demo clip.
# Needs: node + playwright (chromium), ffmpeg, python3 with numpy/scipy, piper-tts and a Piper voice
#   pip install piper-tts; curl -LO https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-ryan-high.tar.gz
# Usage: ./make_video.sh path/to/en-us-ryan-high.onnx [out.mp4]
set -euo pipefail
cd "$(dirname "$0")"; VOICE=$1; OUT=${2:-hridaymitra_pitch.mp4}; W=$(mktemp -d)
python3 voice.py "$VOICE" "$W/vo"                       # writes timing.js: everything below follows it
TOTAL=$(python3 -c "import json;print(json.loads(open('timing.js').read().split('=',1)[1].rstrip(';\n '))['total'])")
read A B < <(python3 -c "import json;T=json.loads(open('timing.js').read().split('=',1)[1].rstrip(';\n '));print(T['cues']['built:4']+.3,T['segs']['built'][1]-.5)")
Q=$(python3 -c "print($TOTAL/4)")
for i in 0 1 2 3; do node render.js "$W/part$i.mp4" 30 $(python3 -c "print($i*$Q)") $(python3 -c "print(($i+1)*$Q)") & done; wait
printf "file '%s'\n" "$W"/part{0,1,2,3}.mp4 > "$W/list.txt"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$W/list.txt" -c copy "$W/silent.mp4"
python3 music.py "$W/music.wav"; python3 mix.py "$W/vo/voice.wav" "$W/music.wav" "$W/mix.wav"
D=$(python3 -c "print($B-$A)")
ffmpeg -y -loglevel error -i "$W/silent.mp4" -ss 14 -t "$D" -i ../demo/hridaymitra_month_demo.mp4 -i "$W/mix.wav" \
  -filter_complex "[1:v]scale=1200:675,format=yuva420p,fade=in:st=0:d=0.5:alpha=1,fade=out:st=$(python3 -c "print($D-.5)"):d=0.5:alpha=1,setpts=PTS-STARTPTS+$A/TB[c];[0:v][c]overlay=360:270:enable='between(t,$A,$B)':eof_action=pass[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
rm -rf "$W"; echo "done: $OUT"
