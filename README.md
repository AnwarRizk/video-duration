# Video Duration Calculator

A small desktop tool for calculating the total playtime of a video collection.

The app lets you add individual videos or a folder of videos, reads each file's
duration with `ffprobe`, and shows totals for duration, file count, average
duration, and total size.

## Features

- Add one or more video files with the built-in file browser.
- Add all supported videos from a selected folder.
- Optional drag-and-drop support when `tkinterdnd2` is installed.
- Search/filter added videos by file name or path.
- Remove selected videos or clear the full list.
- Open a video's containing folder from the right-click menu.
- Displays Arabic file names with basic shaping support.
- Dark Tkinter interface.

## Supported Formats

The tool recognizes these video extensions:

```text
.mp4 .mkv .avi .mov .webm .flv .wmv .m4v .ts .mpg .mpeg .3gp .ogv
```

## Requirements

- Python 3
- Tkinter
- FFmpeg / `ffprobe`
- Optional: `tkinterdnd2` for drag-and-drop support

On Ubuntu/Debian-based Linux systems:

```bash
sudo apt install python3 python3-tk ffmpeg
```

Optional drag-and-drop support:

```bash
python3 -m pip install tkinterdnd2
```

## Usage

Run the app from this folder:

```bash
python3 video_duration.py
```

Then:

1. Click **Add files** to choose individual videos.
2. Click **Add folder** to add supported videos from one folder.
3. Drag videos or folders into the window if `tkinterdnd2` is installed.
4. Use the search box to filter the current list.
5. Select rows and press **Delete**, or click **Remove selected**, to remove them.
6. Right-click a row and choose **Open containing folder** to open its location.

## Notes

- Folder import currently scans only the selected folder, not subfolders.
- Duplicate file paths are ignored.
- Files that `ffprobe` cannot read are shown as `error`.
- The right-click **Open containing folder** action uses `xdg-open`, so it is
  intended for Linux desktop environments.
