# Shitty YT-DLP Helper

A very basic but pretty gui for YTDLP which comes with it and FFMPEG bundled. Has customization for quality, audio only, mp4 output, pretty naming, subtitle embedding, and ffmpeg integration. Built to save you time.

## Features


Literally just making it piss easy to use YTDLP because good programmers are allergic to GUIs and bad ones like me thrive on them.
<img width="330" height="401" alt="{14B3563D-243A-4515-B0AC-C59FADF87C41}" src="https://github.com/user-attachments/assets/e2ffe2b0-3d02-45a0-8b7a-edf8f65f7d14" />

## Requirements

Just run the exe if not building it.

If building (say you're on linux) it should update yt-dlp for you.
- Python 3.8+
- PySide6
- yt-dlp (will be installed automatically)
- FFmpeg (optional, for additional format support)

## Updating

YTDLP updates all the time, for reasons. Just plop the newer version in the same folder. It'll work and if it doesn't I'll gaslight you until you agree it does.

You can also update FFMPEG and drop its exe in here as well. 

This frontend is so basic I doubt it will ever break if it ever works in the first place.

## Usage

1. Run the shitty exe application
2. Enter a video URL in the input field
3. Select your preferred options:
   - **Best Quality**: Download the highest available quality
   - **MP4 Output**: Convert the output to MP4 format
   - **Pretty Naming**: Use human-readable filenames
   - **Audio Only**: Download audio only
   - **Embed Subtitles**: Include subtitles in the output file
   - **Use FFmpeg**: Use FFmpeg for additional format support (If you turn this off glhf)
4. Click "GET 'EM" to start the download

## Notes

- The application requires an internet connection to download videos
- Some video platforms may have restrictions on downloading content


## License

This project is provided as-is without any warranty. Use at your own risk.

### Third-Party Software Licenses

This application bundles or depends on the following third-party software:

#### yt-dlp
- **License**: The Unlicense (Public Domain)
- **Source**: https://github.com/yt-dlp/yt-dlp
- **License Text**:
  ```
  This is free and unencumbered software released into the public domain.
  
  Anyone is free to copy, modify, publish, use, compile, sell, or
  distribute this software, either in source code form or as a compiled
  binary, for any purpose, commercial or non-commercial, and by any
  means.
  
  For more information, please refer to <https://unlicense.org>
  ```

#### FFmpeg (when bundled)
- **License**: LGPL v2.1 or later
- **Source**: https://ffmpeg.org/
- **Note**: FFmpeg is ~not~ included in this distribution but may be used if present in the system PATH. If you choose to distribute FFmpeg with this application, you must comply with the LGPL v2.1+ license terms.

#### PySide6
- **License**: LGPL v3
- **Source**: https://pypi.org/project/PySide6/
- **Note**: This application uses PySide6 for its GUI, which is licensed under the LGPL v3. The LGPL allows dynamic linking with proprietary software.
