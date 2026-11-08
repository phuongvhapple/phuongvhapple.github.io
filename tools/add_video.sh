#!/bin/zsh
# Web copy of a project video plus its poster, both in assets/video/.
#
#   tools/add_video.sh <source.mp4> <name> [poster second] [crf]
#
#   name         file name without extension, e.g. dlvn-dlympic-2022
#   poster       second of the frame used as the poster (default 2)
#   crf          27 for short UI films (default), 28 for long event films
#
# Keep the original in Images/<FOLDER>/_videos/. If the web copy comes out bigger than the
# source (sources downloaded from YouTube are already tightly compressed), the script keeps
# the source stream instead and only moves its index to the front so it starts playing at once.
# Then list it on the project in portfolio.src.html:
#   videos: [["Title", "assets/video/<name>.mp4", "assets/video/<name>.webp"]]
# add a 4th item `true` when the file is over 15 MB (the artifact links to the live site then).
set -e
cd "$(dirname "$0")/.."
src="$1"; name="$2"; t="${3:-2}"; crf="${4:-27}"
[ -f "$src" ] && [ -n "$name" ] || { echo "usage: tools/add_video.sh <source.mp4> <name> [poster second] [crf]"; exit 1; }
out="assets/video/$name.mp4"
ffmpeg -nostdin -y -loglevel error -i "$src" -c:v libx264 -crf "$crf" -preset slow -pix_fmt yuv420p \
  -movflags +faststart -c:a aac -b:a 128k "$out"
if [ "$(stat -f%z "$out")" -ge "$(stat -f%z "$src")" ]; then
  ffmpeg -nostdin -y -loglevel error -i "$src" -c copy -movflags +faststart "$out"
  echo "kept the source stream (re-encoding made it bigger)"
fi
ffmpeg -nostdin -y -loglevel error -ss "$t" -i "$src" -frames:v 1 -vf scale=1280:-2 -f image2pipe -vcodec png - \
  | .venv/bin/python -c "import sys,io; from PIL import Image; Image.open(io.BytesIO(sys.stdin.buffer.read())).convert('RGB').save(sys.argv[1],'WEBP',quality=82,method=6)" "assets/video/$name.webp"
echo "$out $(du -m "$out" | cut -f1) MB, poster assets/video/$name.webp"
