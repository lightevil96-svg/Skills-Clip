# Render and production workflow

This reference adds the practical delivery constraints used in the project. Apply them when the user asks for an editable render package or wants to render on their own PC/Google Colab.

## 1. Inspect before editing

Use FFprobe to record all stream timing, not just container duration:

```bash
ffprobe -v error \
  -show_entries format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,start_time,duration \
  -of json INPUT.mp4
```

Then:

1. Generate a contact sheet at 1 fps for the whole clip.
2. Generate denser frames (2–4 fps or individual PNGs) around likely cuts, speaker changes, and visual gags.
3. Inspect full frames before selecting crop coordinates.
4. Check audio levels and waveform. If speech recognition is available, verify the result manually. Never use an unverified transcript as exact subtitles.
5. Keep stream timestamps consistent when trimming and concatenating. Check `start_time` for each stream; do not assume video and audio necessarily begin together.

## 2. Build the edit non-destructively

- Keep the original source video outside the deliverable package.
- Use a script that accepts the source video path as an argument. For example: `./render.sh /path/to/source.mp4` or drag the source file onto `render.bat`.
- Store only generated overlays, masks, fonts/assets that may be redistributed, audio assets if used, scripts, and instructions.
- Prefer an inline filter graph with `-filter_complex`. Check the actual build's filters and encoders; command form alone does not prove compatibility across FFmpeg versions.
- For animated transparent overlays, render frames to FFmpeg and use FFV1 in a Matroska `.mkv` with alpha (BGRA) when appropriate. Do not use huge uncompressed animation formats without a reason.
- Keep static full-frame assets such as a vignette as separate image inputs rather than baking them into every overlay frame when that improves compression.
- Normalize segment properties before concatenation: frame rate, pixel format, sample aspect ratio, audio sample rate, and channel layout must match.

## 3. Render defaults

Unless the user requests another format:

- Canvas: 1080×1920 (9:16).
- Frame rate: match the actual source. Use 30 fps only when the source or an explicit project decision supports it; the sample's frame rate is not universal.
- Video: H.264, `yuv420p`, square pixels (`setsar=1`), fast-start enabled.
- Audio: AAC, 48 kHz, stereo.
- Keep the original voice synchronized and intelligible.
- Add BGM only when requested or when it clearly helps. If added, duck it under speech. Add SFX only for an evidenced event or editorial purpose; a cut alone does not justify sound.
- Keep captions and graphic overlays on a separate transparent layer when that makes revision easier.

Do not assume the sample's 360×640 resolution is the desired output resolution. It is only the resolution of the supplied reference file.

## 4. Package structure

A typical ZIP can contain:

```text
clip-package/
├── render.sh
├── render.bat
├── overlay.mkv          # only if an animated overlay is needed
├── music.flac           # only if music is used
├── sfx.flac             # only if sound effects are used
├── assets/
│   ├── masks or stickers
│   └── static graphics
└── BACA_DULU.txt
```

Do not include the user's source video in the ZIP. The script must accept a user-supplied path instead of depending on a hard-coded source filename.

Keep the README/guide short and explicit:

1. Install or verify FFmpeg.
2. Extract the ZIP.
3. Put the source video where the user can select it.
4. Run the script with the source path.
5. Find the output file and check its size before downloading.

## 5. Google Colab and mobile guidance

When the user renders from a phone:

- Prefer Colab CPU unless a specific GPU encoder/filter has been tested. The described FFmpeg filter workflow is generally CPU-bound; a GPU runtime does not automatically make it faster.
- Prefer uploading through Colab's Files panel or mounting Google Drive. The in-cell `files.upload()` widget can be unreliable on mobile browsers.
- Avoid requiring multiple browser tabs during upload.
- After uploading the ZIP, check its size before extraction. A truncated ZIP should be uploaded again.
- Give a copyable extraction and render command, for example:

```bash
!unzip -oq CLIP_PACKAGE.zip
!cd CLIP_PACKAGE && bash render.sh /content/SOURCE_VIDEO.mp4
```

- Tell the user to download the rendered MP4 from the Files panel or with Colab's download helper.
- Warn that Colab runtime files disappear when the session ends; move the finished render to Drive if it must be kept.

## 6. Compatibility and common failure points

- Record the tested FFmpeg version and required filters/encoders. Treat other builds as NOT_RUN until tested; prefer inline filter graphs.
- Use Bash for scripts that depend on process substitution or Bash-specific syntax; do not invoke those scripts with plain `sh`.
- In Windows batch files, escape percent signs as `%%` and use `^` for line continuation.
- Keep the Windows command line under the 8191-character limit. If a filter graph approaches that limit, simplify it rather than relying on deprecated script-file filters.
- When using looped still images (`-loop 1`), bound the output duration explicitly with `-t`.
- Before `concat`, make every video segment use matching `fps`, `format=yuv420p`, and `setsar=1`; make audio segments use the same sample rate and channel layout.
- Do not assume that the presence of a GPU speeds up CPU filters or software encoding.

## 7. Quality-control pass

Do a short test render before packaging. Inspect:

- opening frame and first caption;
- every speaker change;
- every meme/sticker entrance and exit;
- any flash, blur, zoom, or two-shot;
- final reaction and last frame;
- audio/video synchronization;
- subtitle spelling, timing, contrast, and speaker color;
- output duration, resolution, frame rate, audio codec, and file size.

A successful FFmpeg exit code is not enough. Review the actual rendered frames and listen to the output before calling the package finished.
