# TuneCollector - Radio Playlist Scraper & Downloader

**TuneCollector** is a feature-rich command-line tool to scrape playlist data from **100+ German radio channels** on myonlineradio.de and **download songs directly from YouTube** as MP3/MP4. Features a beautiful rich CLI interface with progress bars, colored output, ID3 metadata tagging, and flexible configuration options.

## Features

🎵 **Multi-Channel Support**
- Works with 100+ German radio channels
- Popular channels: 1LIVE, Antenne Bayern, Bayern 3, SWR4, NDR 2, WDR 2, BigFM, and many more
- Easy channel selection with `--channel/-c` flag
- List all available channels with `--list-channels`

🎧 **YouTube Download**  
- Download songs as MP3, M4A, or MP4
- Configurable audio quality (128/192/320 kbps or best)
- Automatic ID3 metadata tagging (artist, title, album)
- Smart filename handling — skips already downloaded songs by default
- Always downloads unique songs only (no duplicate downloads)
- Two modes: Live (during scraping) or Batch (from CSV)
- Progress bars and error handling

✨ **Rich CLI Interface**
- Beautiful progress bars during scraping and downloading
- Colored status messages (success, warning, error)
- Summary tables showing statistics per channel
- Sample track display

🎯 **Flexible Output Options**
- Save all songs
- Save unique songs only (by YouTube ID)
- Save both all and unique to separate files
- Auto-generated filenames per channel (e.g., `1live_playlist.csv`)

⚙️ **Configurable Limits**
- Set maximum pages to scrape
- Limit total number of songs
- Customize starting ID for pagination

🎨 **Multiple Modes**
- Interactive mode with guided prompts
- Command-line argument mode
- Quiet mode for minimal output
- No-color mode for simple terminals

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### List Available Channels

```bash
python3 scraper.py --list-channels
```

This shows all 100+ available German radio channels including:
- **1LIVE** (WDR) - Pop/Rock
- **Antenne Bayern** - Hit Radio
- **Bayern 3** - Pop/Rock
- **SWR4** - Oldies/Classics
- **NDR 2** - Pop
- **WDR 2** - Pop/Info
- **BigFM** - Hip Hop/R&B
- **DASDING** (SWR) - Alternative/Indie
- And 60+ more channels!

### Interactive Mode (Recommended for first-time users)

```bash
python3 scraper.py
# or
python3 scraper.py --interactive
```

The interactive mode will guide you through configuration options with prompts.

### Command-Line Mode

#### Multi-Channel Examples

```bash
# Scrape 1LIVE
python3 scraper.py -c 1live -p 5

# Scrape Antenne Bayern, save unique songs only
python3 scraper.py -c antenne-bayern -p 3 --unique-only

# Scrape Bayern 3, max 100 songs, save both versions
python3 scraper.py -c bayern-3 -n 100 --save-both

# Scrape NDR 2 with custom output
python3 scraper.py -c ndr-2 -p 5 -o my_ndr_songs.csv

# Scrape WDR 2 in quiet mode
python3 scraper.py -c wdr2 -p 10 -q

# Default to SWR4 (backward compatible)
python3 scraper.py -p 5
```

#### YouTube Download Examples

**Download during scraping (Live Mode):**
```bash
# Scrape and download as MP3 (192 kbps)
python3 scraper.py -c 1live -p 5 --download

# Download with specific quality
python3 scraper.py -c bayern-3 -p 3 --download --quality 320

# Download as M4A (better quality)
python3 scraper.py -c bigfm -n 50 --download --format m4a --quality best

# Download unique songs only
python3 scraper.py -c swr4 -p 10 --unique-only --download

# Download to custom directory
python3 scraper.py -c ndr-2 -p 5 --download --download-dir ./my_music

# Download without metadata (faster)
python3 scraper.py -c antenne-bayern -p 3 --download --no-metadata
```

**Download from existing CSV (Batch Mode):**
```bash
# Download songs from a previously scraped playlist
python3 scraper.py --from-csv 1live_playlist.csv --download

# Download unique songs only from CSV
python3 scraper.py --from-csv bayern-3_playlist.csv --unique-only --download

# High quality downloads from CSV
python3 scraper.py --from-csv swr4_playlist.csv --download --quality 320

# Download as MP4 video
python3 scraper.py --from-csv bigfm_playlist.csv --download --format mp4
```

#### Basic Examples

```bash
# Scrape 5 pages, save all songs (default: SWR4)
python3 scraper.py -p 5

# Scrape 3 pages, save only unique songs
python3 scraper.py -p 3 --unique-only

# Scrape up to 100 songs, save both all and unique versions
python3 scraper.py -n 100 --save-both

# Custom output filename
python3 scraper.py -p 5 -o my_playlist.csv

# Quiet mode (minimal output)
python3 scraper.py -p 10 -q
```

#### Advanced Multi-Channel Examples

```bash
# Compare playlists across multiple channels
python3 scraper.py -c 1live -p 5 -o 1live.csv
python3 scraper.py -c bayern-3 -p 5 -o bayern3.csv
python3 scraper.py -c ndr-2 -p 5 -o ndr2.csv

# Large scrape with unique filtering
python3 scraper.py -c swr3 -p 20 --unique-only

# Quick test of a new channel
python3 scraper.py -c radio-hamburg -p 1 -n 10
```

#### Advanced Examples

```bash
# Scrape 10 pages with max 200 songs, save unique only
python3 scraper.py -p 10 -n 200 --unique-only -o unique_songs.csv

# Scrape with custom starting ID (for resuming)
python3 scraper.py -p 5 --start-id 672398913

# Disable colored output (for piping or simple terminals)
python3 scraper.py -p 3 --no-color

# Scrape many pages, save both versions, quiet mode
python3 scraper.py -p 20 --save-both -q
```

### Command-Line Options

**General Options:**
```
-h, --help              Show help message and exit
-c, --channel CHANNEL   Radio channel to scrape (default: swr4)
--list-channels         Show all available radio channels and exit
-p, --pages N           Maximum number of pages to scrape (default: 3)
-n, --max-songs N       Maximum number of songs to download
-o, --output FILE       Output filename (default: {channel}_playlist.csv)
--start-id ID           Starting lastId parameter (optional)
--unique-only           Save only unique songs (by youtube_id)
--save-both             Save both all songs and unique songs to separate files
-q, --quiet             Minimal output mode (no progress bars)
--no-color              Disable colored output
-i, --interactive       Interactive mode with guided prompts
```

**YouTube Download Options:**
```
--download              Enable YouTube downloads
--format FORMAT         Download format: mp3, m4a, mp4 (default: mp3)
--quality QUALITY       Audio quality: 128, 192, 320, best (default: 192)
--download-dir DIR      Download directory (default: downloads/)
--from-csv FILE         Download from existing CSV file instead of scraping
--redownload            Re-download files that already exist (default: skip existing)
--no-metadata           Skip ID3 metadata embedding (faster)
```

## Available Channels

The scraper supports **100+ German radio stations** including:

### Popular Channels
- **1LIVE** (WDR) - Pop, Rock, Alternative
- **Antenne Bayern** - Hit Radio
- **Bayern 1** - Regional, Oldies
- **Bayern 3** - Pop, Rock
- **BigFM** - Hip Hop, R&B, Dance
- **DASDING** (SWR) - Alternative, Indie
- **Deutschlandfunk** - News, Talk
- **HIT RADIO FFH** - Pop, Hits
- **Kiss FM** - Hip Hop, R&B
- **Klassik Radio** - Classical Music
- **MDR JUMP** - Pop, Rock
- **NDR 2** - Pop, Rock
- **N-JOY** - Pop, Dance, Electronic
- **Radio Hamburg** - Regional Pop
- **SWR1** - Oldies, Classics
- **SWR3** - Pop, Rock
- **SWR4** - Oldies, Classics, Schlager
- **WDR 2** - Pop, Info

### All Channels
Use `--list-channels` to see the complete list of 100+ available channels including regional stations, genre-specific channels, and more!

## Output

### CSV File Format

All CSV files contain the following columns:
- `timestamp`: When the song played (e.g., "24.02 14:55" or "LIVE - 24.02 14:55")
- `artist`: Artist/band name  
- `song`: Song title
- `youtube_id`: YouTube video ID from the `data-youtube` attribute
- `data_id`: Internal playlist ID

### File Naming

- **Default mode**: `{channel}_playlist.csv` (e.g., `1live_playlist.csv`, `bayern-3_playlist.csv`)
- **Custom output**: Use `-o` to specify your own filename
- **--save-both mode**: Creates two files:
  - `{channel}_playlist_all.csv` - All scraped songs
  - `{channel}_playlist_unique.csv` - Unique songs only

### Duplicate Detection

The `--unique-only` and `--save-both` modes filter duplicates based on the `youtube_id` field. When duplicates are found, the first occurrence (earliest in scraping order) is kept.

## Examples of Output

### Multi-Channel Scraping
```
Scraping BAYERN-3 playlist...
Initializing session and getting cookies...
✓ Session initialized
⠋ Scraping BAYERN-3 pages... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  50%
✓ Saved unique songs to bayern-3_playlist.csv

      Scraping Summary - BAYERN-3       
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric                    ┃    Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Channel                   │ BAYERN-3 │
│ Pages Scraped             │        2 │
│ Total Songs Found         │       90 │
│ Unique Songs              │       32 │
│ Duplicates Removed        │       58 │
└───────────────────────────┴──────────┘
```

### Regular Mode
```
Initializing session and getting cookies...
✓ Session initialized
⠋ Scraping pages... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  50%
✓ Saved all songs to swr4_playlist.csv

            Scraping Summary            
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric                    ┃    Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Pages Scraped             │        3 │
│ Total Songs Found         │      135 │
│ Unique Songs              │       68 │
│ Duplicates Removed        │       67 │
└───────────────────────────┴──────────┘
```

### Quiet Mode
```
✓ Saved all songs to swr4_playlist.csv
```

## Tips

**Scraping:**
- **Start with --list-channels**: Browse available channels before scraping
- **Try different channels**: Each station has different music styles and playlists
- **Start small**: Try `-p 2` or `-n 20` first to test a new channel
- **Use --save-both**: Keep statistics with all data while having a clean unique list
- **Interactive mode**: Great for exploring options without memorizing flags
- **Quiet mode**: Perfect for cron jobs or when you only care about the output file
- **Song limit**: Use `-n` when you want a specific number of songs regardless of pages
- **Auto-naming**: Let the tool name files by channel (omit `-o` flag)

**Downloading:**
- **Test first**: Download 2-3 songs first to verify everything works
- **Use --unique-only**: Avoid downloading duplicates
- **Quality vs Size**: 192 kbps is a good balance, 320 kbps for best quality
- **Batch mode**: Scrape first, then download - allows you to review the list
- **Format choice**: MP3 is most compatible, M4A has better quality at same bitrate
- **Skip by default**: Already downloaded songs are skipped automatically — use `--redownload` to force re-downloading
- **No duplicate downloads**: Only unique songs (by YouTube ID) are ever downloaded, regardless of save mode
- **Network**: Downloads can be large (3-5 MB per song) - use Wi-Fi!

## Troubleshooting

### Channel Not Found
If you get a 404 error:
- Use `--list-channels` to verify the channel ID
- Channel IDs are case-insensitive but use hyphens (e.g., `bayern-3`, not `bayern3`)

### YouTube Downloads Failing
If downloads fail:
- **Video unavailable**: The video may have been removed or is geo-blocked
- **Private video**: Some videos are private or require login
- **Rate limiting**: YouTube may temporarily block requests - wait a few minutes
- **FFmpeg required**: Make sure FFmpeg is installed for format conversion
- **Network issues**: Check your internet connection

### Rate Limiting
The scraper includes automatic 1-2 second delays between page requests to be respectful to the server.

### Cloudflare Protection
The scraper handles Cloudflare protection by:
1. Visiting the main page first to get cookies
2. Using realistic browser headers
3. Maintaining a session across requests

### No Songs Found
If you get zero songs:
- Check your internet connection
- Try a different channel with `--list-channels`
- The playlist might be temporarily unavailable
- Some channels may have different HTML structures (most work though!)

## Project Structure

```
TuneCollector/
├── scraper.py              # Main scraper script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE.md             # GPL v3 License
└── .gitignore             # Git ignore rules
```

## Legal & Disclaimers

### Terms of Use
This tool is provided for educational and personal use only. Users are responsible for:
- Complying with YouTube's Terms of Service
- Respecting copyright laws and intellectual property rights
- Following myonlineradio.de's terms and conditions
- Using the tool responsibly and ethically

### Important Notes
- **Copyright**: Downloaded content may be copyrighted. Ensure you have the right to download and use the content.
- **YouTube ToS**: Downloading from YouTube may violate their Terms of Service. Use at your own risk.
- **Rate Limiting**: The scraper includes delays to be respectful to servers. Do not modify these to avoid server overload.
- **No Warranty**: This software is provided "as is" without warranty of any kind.
- **Personal Use**: This tool is intended for personal, non-commercial use only.

### Created with AI Assistance
This project was developed with assistance from AI (GitHub Copilot CLI). The code has been reviewed, tested, and validated to ensure functionality and quality.

## Credits

**Data Source:** [myonlineradio.de](https://myonlineradio.de/) - A comprehensive directory of German online radio stations with playlist tracking.

**Technologies:**
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download library
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Mutagen](https://github.com/quodlibet/mutagen) - Audio metadata handling

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

See [LICENSE.md](LICENSE.md) for details.

**Key Points:**
- ✅ Free to use, modify, and distribute
- ✅ Source code must be made available
- ✅ Modifications must also be GPL-3.0
- ✅ No warranty provided

---

**⚠️ Use Responsibly**: Always respect copyright laws, terms of service, and intellectual property rights when using this tool.
