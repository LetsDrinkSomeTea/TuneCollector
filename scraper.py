#!/usr/bin/env python3
"""
MyOnlineRadio Playlist Scraper & Downloader
Scrapes playlist data from myonlineradio.de with support for 100+ German radio channels
Optionally downloads songs from YouTube as MP3/MP4

Copyright (C) 2024  Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

---
DISCLAIMER:
This tool is for educational and personal use only. Users are responsible for:
- Complying with YouTube's Terms of Service
- Respecting copyright laws and intellectual property rights
- Following myonlineradio.de's terms and conditions
- Using the tool responsibly and ethically

Downloaded content may be copyrighted. Ensure you have the right to download
and use the content. The authors assume no liability for misuse.

This project was developed with assistance from AI (GitHub Copilot CLI).
---
"""

import argparse
import requests
from bs4 import BeautifulSoup
import csv
import sys
import time
import re
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB
from mutagen.mp3 import MP3

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, DownloadColumn, TimeRemainingColumn
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich import print as rprint

# Initialize console
console = Console()

# Popular German radio channels on myonlineradio.de
POPULAR_CHANNELS = {
    '1live': '1LIVE (WDR)',
    'antenne-bayern': 'Antenne Bayern',
    'bayern-1': 'Bayern 1',
    'bayern-3': 'Bayern 3',
    'bigfm': 'bigFM',
    'dasding': 'DASDING (SWR)',
    'deutschlandfunk': 'Deutschlandfunk',
    'hit-radio-ffh': 'HIT RADIO FFH',
    'hr1': 'hr1',
    'hr3': 'hr3',
    'kiss-fm': 'KISS FM',
    'klassik-radio': 'Klassik Radio',
    'mdr-jump': 'MDR JUMP',
    'ndr-2': 'NDR 2',
    'n-joy': 'N-JOY',
    'radio-hamburg': 'Radio Hamburg',
    'swr1': 'SWR1',
    'swr3': 'SWR3',
    'swr4': 'SWR4',
    'wdr2': 'WDR 2',
}

# Extended list of all available channels (100+)
ALL_CHANNELS = [
    '1live', '1live-diggi', '80s80s', '90s90s', 'absolut-radio', 'antenne-ac',
    'antenne-bayern', 'b5-aktuell', 'baden-fm', 'bayern-1', 'bayern-2', 'bayern-3',
    'bayernwelle', 'bigfm', 'br-heimat', 'br-klassik', 'brocken-fm', 'dasding',
    'deutschlandfunk', 'deutschlandfunk-kultur', 'deutschlandfunk-nova', 'die-neue-107-7',
    'energy-muenchen', 'ffh', 'flex-fm', 'gong-96-3', 'harmonie-fm', 'hit-radio-ffh',
    'hitradio-rtl', 'hr1', 'hr2', 'hr3', 'hr4', 'iloveradio', 'jam-fm', 'klassik-radio',
    'kiss-fm', 'landeswelle', 'mdr-jump', 'mdr-sachsen', 'mdr-thueringen', 'metropol-fm',
    'ndr-1-niedersachsen', 'ndr-1-welle-nord', 'ndr-2', 'ndr-info', 'n-joy', 'nordwestradio',
    'radio-7', 'radio-21', 'radio-bob', 'radio-hamburg', 'radio-paloma', 'radio-salue',
    'radioeins', 'rock-antenne', 'rockland-radio', 'rsh', 'rt1', 'star-fm', 'sunshine-live',
    'swr1', 'swr2', 'swr3', 'swr4', 'wdr2', 'wdr3', 'wdr4', 'wdr5', 'you-fm',
]


def scrape_playlist(
    session: requests.Session, channel: str = 'swr4', act_page: int = 1, 
    last_id: str = "", progress: Optional[Progress] = None, task_id: Optional[int] = None
) -> List[Dict[str, str]]:
    """
    Scrape playlist data from myonlineradio.de

    Args:
        session: Requests session with cookies
        channel: Radio channel name (e.g., 'swr4', '1live', 'bayern-3')
        act_page: Page number to scrape
        last_id: Last ID parameter for pagination
        progress: Optional rich Progress instance
        task_id: Optional task ID for progress tracking

    Returns:
        List of dictionaries containing artist, song, youtube_id, timestamp, and data_id
    """
    url = f"https://myonlineradio.de/{channel}/playlist"
    params = {
        "ajax": "1",
        "name": "",
        "from": "",
        "to": "",
        "actPage": str(act_page),
        "lastId": last_id,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        "Referer": "https://myonlineradio.de/swr4/playlist",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        if progress and task_id is not None:
            progress.update(task_id, description=f"[cyan]Scraping page {act_page}...")
        
        response = session.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all playlist items with data-youtube attribute
        playlist_items = soup.find_all(attrs={"data-youtube": True})

        results = []
        for item in playlist_items:
            youtube_id = item.get("data-youtube")
            data_id = item.get("data-id")

            # Extract artist
            artist_elem = item.find("span", itemprop="byArtist")
            artist = artist_elem.get_text(strip=True) if artist_elem else ""

            # Extract song name
            song_elem = item.find("span", itemprop="name")
            song = song_elem.get_text(strip=True) if song_elem else ""

            # Extract timestamp
            time_elem = item.find("span", class_="txt2 mcolumn")
            timestamp = time_elem.get_text(strip=True) if time_elem else ""

            if artist or song:  # Only add if we found at least artist or song
                results.append(
                    {
                        "timestamp": timestamp,
                        "artist": artist,
                        "song": song,
                        "youtube_id": youtube_id,
                        "data_id": data_id,
                    }
                )

        if progress and task_id is not None:
            progress.update(task_id, advance=1, description=f"[green]✓ Page {act_page} ({len(results)} tracks)")
        
        return results

    except requests.RequestException as e:
        if progress and task_id is not None:
            progress.update(task_id, description=f"[red]✗ Page {act_page} failed")
        console.print(f"[red]Error fetching page {act_page}: {e}[/red]")
        return []


def filter_unique_songs(data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Filter songs to keep only unique entries based on youtube_id.
    Keeps the first occurrence of each unique youtube_id.
    
    Args:
        data: List of song dictionaries
        
    Returns:
        List of unique songs
    """
    seen_ids = set()
    unique_songs = []
    
    for song in data:
        youtube_id = song.get('youtube_id')
        if youtube_id and youtube_id not in seen_ids:
            seen_ids.add(youtube_id)
            unique_songs.append(song)
    
    return unique_songs


def save_to_csv(data: List[Dict[str, str]], filename: str = "swr4_playlist.csv") -> bool:
    """Save scraped data to CSV file"""
    if not data:
        console.print("[yellow]No data to save[/yellow]")
        return False

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["timestamp", "artist", "song", "youtube_id", "data_id"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(data)

        return True
    except Exception as e:
        console.print(f"[red]Error saving to {filename}: {e}[/red]")
        return False


def list_channels():
    """Display available radio channels"""
    console.print(Panel.fit(
        "[bold cyan]Available Radio Channels[/bold cyan]\n"
        f"Total: {len(ALL_CHANNELS)} channels",
        border_style="cyan"
    ))
    
    # Show popular channels first
    console.print("\n[bold yellow]Popular Channels:[/bold yellow]")
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    
    for channel_id, channel_name in sorted(POPULAR_CHANNELS.items()):
        table.add_row(channel_id, channel_name)
    
    console.print(table)
    
    # Show all channels in compact format
    console.print("\n[bold yellow]All Channels:[/bold yellow]")
    console.print("[dim]Use any of these channel IDs with --channel/-c[/dim]\n")
    
    # Print in columns
    channels_per_row = 4
    for i in range(0, len(ALL_CHANNELS), channels_per_row):
        row_channels = ALL_CHANNELS[i:i+channels_per_row]
        console.print("  ".join(f"[cyan]{ch:20s}[/cyan]" for ch in row_channels))
    
    console.print(f"\n[dim]Total: {len(ALL_CHANNELS)} channels available[/dim]")


def validate_channel(channel: str) -> bool:
    """Check if a channel is valid"""
    return channel.lower() in ALL_CHANNELS


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters: / \ : * ? " < > |
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Trim whitespace and dots from ends
    sanitized = sanitized.strip(' .')
    
    # Limit length to 200 chars (leave room for extension and numbering)
    if len(sanitized) > 200:
        sanitized = sanitized[:200].strip()
    
    return sanitized if sanitized else 'untitled'


def get_unique_filename(directory: Path, base_name: str, extension: str) -> Path:
    """
    Get a unique filename by appending numbers if file exists.
    
    Args:
        directory: Target directory
        base_name: Base filename without extension
        extension: File extension (e.g., '.mp3')
        
    Returns:
        Unique file path
    """
    filename = directory / f"{base_name}{extension}"
    
    if not filename.exists():
        return filename
    
    # File exists, append number
    counter = 1
    while True:
        filename = directory / f"{base_name} ({counter}){extension}"
        if not filename.exists():
            return filename
        counter += 1
        if counter > 1000:  # Safety limit
            raise Exception("Too many duplicate filenames")


def download_youtube_audio(
    youtube_id: str,
    artist: str,
    song: str,
    channel: str,
    download_dir: Path,
    format_choice: str = 'mp3',
    quality: str = '192',
    add_metadata: bool = True,
    progress: Optional[Progress] = None,
    task_id: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Download audio from YouTube and optionally add metadata.
    
    Args:
        youtube_id: YouTube video ID
        artist: Artist name
        song: Song title
        channel: Radio channel name
        download_dir: Download directory
        format_choice: Output format (mp3, m4a, mp4)
        quality: Audio quality (128, 192, 320, best)
        add_metadata: Whether to embed ID3 tags
        progress: Optional rich Progress instance
        task_id: Optional task ID for progress tracking
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Create download directory if it doesn't exist
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        if artist and song:
            base_filename = sanitize_filename(f"{artist} - {song}")
        elif song:
            base_filename = sanitize_filename(song)
        elif artist:
            base_filename = sanitize_filename(artist)
        else:
            base_filename = sanitize_filename(youtube_id)
        
        # Determine extension
        ext_map = {'mp3': '.mp3', 'm4a': '.m4a', 'mp4': '.mp4'}
        extension = ext_map.get(format_choice, '.mp3')
        
        # Get unique filename
        output_path = get_unique_filename(download_dir, base_filename, extension)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_path.with_suffix('')),  # yt-dlp adds extension
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
        }
        
        # Add format-specific options
        if format_choice in ['mp3', 'm4a']:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_choice,
                'preferredquality': quality if quality != 'best' else '0',
            }]
        
        # Download
        url = f"https://www.youtube.com/watch?v={youtube_id}"
        
        if progress and task_id is not None:
            progress.update(task_id, description=f"[cyan]Downloading: {base_filename[:40]}...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Add metadata if requested and format is MP3
        if add_metadata and format_choice == 'mp3' and output_path.exists():
            try:
                audio = MP3(str(output_path), ID3=ID3)
                
                # Add ID3 tag if it doesn't exist
                try:
                    audio.add_tags()
                except:
                    pass
                
                # Set tags
                if artist:
                    audio['TPE1'] = TPE1(encoding=3, text=artist)
                if song:
                    audio['TIT2'] = TIT2(encoding=3, text=song)
                if channel:
                    audio['TALB'] = TALB(encoding=3, text=channel.upper())
                
                audio.save()
            except Exception as e:
                # Metadata failed but download succeeded
                console.print(f"[yellow]⚠ Metadata error for {base_filename[:30]}: {str(e)[:50]}[/yellow]")
        
        if progress and task_id is not None:
            progress.update(task_id, advance=1)
        
        return True, f"✓ {base_filename[:50]}"
        
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'unavailable' in error_msg.lower():
            return False, f"✗ Unavailable: {base_filename[:40]}"
        elif 'private' in error_msg.lower():
            return False, f"✗ Private: {base_filename[:40]}"
        else:
            return False, f"✗ Error: {base_filename[:40]}"
    
    except Exception as e:
        return False, f"✗ Failed: {base_filename[:40]} ({str(e)[:30]})"


def load_songs_from_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    Load song data from CSV file.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        List of song dictionaries
    """
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            songs = list(reader)
            return songs
    except Exception as e:
        console.print(f"[red]Error loading CSV: {e}[/red]")
        return []


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="MyOnlineRadio Playlist Scraper - Download playlist data from 100+ German radio channels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-channels                       # Show all available channels
  %(prog)s -c 1live -p 5 --unique-only           # Scrape 1LIVE
  %(prog)s -c antenne-bayern -p 10 --save-both   # Scrape Antenne Bayern
  %(prog)s -c bayern-3 -n 100                    # Scrape Bayern 3, max 100 songs
  %(prog)s -p 5                                  # Scrape SWR4 (default)

Popular channels: 1live, antenne-bayern, bayern-3, bigfm, ndr-2, swr3, wdr2
        """
    )
    
    parser.add_argument('-c', '--channel', type=str, default='swr4',
                        help='Radio channel to scrape (default: swr4). Use --list-channels to see all.')
    parser.add_argument('--list-channels', action='store_true',
                        help='Show all available radio channels and exit')
    parser.add_argument('-p', '--pages', type=int, default=3,
                        help='Maximum number of pages to scrape (default: 3)')
    parser.add_argument('-n', '--max-songs', type=int, metavar='N',
                        help='Maximum number of songs to download (optional)')
    parser.add_argument('-o', '--output', type=str, default='',
                        help='Output filename (default: {channel}_playlist.csv)')
    parser.add_argument('--start-id', type=str, default='',
                        help='Starting lastId parameter (optional)')
    
    # Output mode options (mutually exclusive group)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('--unique-only', action='store_true',
                              help='Save only unique songs (by youtube_id)')
    output_group.add_argument('--save-both', action='store_true',
                              help='Save both all songs and unique songs to separate files')
    
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Minimal output mode (no progress bars)')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Interactive mode with guided prompts')
    
    # YouTube download options
    parser.add_argument('--download', action='store_true',
                        help='Enable YouTube downloads')
    parser.add_argument('--format', type=str, choices=['mp3', 'm4a', 'mp4'], default='mp3',
                        help='Download format (default: mp3)')
    parser.add_argument('--quality', type=str, choices=['128', '192', '320', 'best'], default='192',
                        help='Audio quality in kbps (default: 192)')
    parser.add_argument('--download-dir', type=str, default='downloads',
                        help='Download directory (default: downloads/)')
    parser.add_argument('--from-csv', type=str, metavar='FILE',
                        help='Download from existing CSV file instead of scraping')
    parser.add_argument('--skip-existing', action='store_true',
                        help="Don't re-download existing files")
    parser.add_argument('--no-metadata', action='store_true',
                        help='Skip ID3 metadata embedding (faster)')
    
    return parser.parse_args()


def get_interactive_config() -> dict:
    """Get configuration through interactive prompts"""
    console.print(Panel.fit(
        "[bold cyan]MyOnlineRadio Playlist Scraper[/bold cyan]\n"
        "Interactive Configuration",
        border_style="cyan"
    ))
    
    # Channel selection
    console.print("\n[cyan]Select a radio channel:[/cyan]")
    console.print("[dim]Popular channels:[/dim]")
    for i, (ch_id, ch_name) in enumerate(list(POPULAR_CHANNELS.items())[:10], 1):
        console.print(f"  {i:2d}. {ch_name:25s} ({ch_id})")
    console.print("  Or enter any channel ID manually")
    
    channel_choice = Prompt.ask("\n[cyan]Channel ID or number[/cyan]", default="swr4")
    
    # If numeric, map to popular channel
    if channel_choice.isdigit():
        idx = int(channel_choice) - 1
        popular_list = list(POPULAR_CHANNELS.keys())
        if 0 <= idx < len(popular_list):
            channel = popular_list[idx]
        else:
            channel = 'swr4'
    else:
        channel = channel_choice.lower()
    
    # Validate channel
    if not validate_channel(channel):
        console.print(f"[yellow]Warning: '{channel}' not in known channels list. Will try anyway.[/yellow]")
    
    pages = IntPrompt.ask("[cyan]How many pages to scrape?[/cyan]", default=3)
    
    use_max_songs = Confirm.ask("[cyan]Do you want to limit the number of songs?[/cyan]", default=False)
    max_songs = None
    if use_max_songs:
        max_songs = IntPrompt.ask("[cyan]Maximum number of songs[/cyan]")
    
    output = Prompt.ask("[cyan]Output filename (leave empty for auto)[/cyan]", default="")
    
    console.print("\n[cyan]Output mode:[/cyan]")
    console.print("1. Save all songs")
    console.print("2. Save unique songs only")
    console.print("3. Save both (all and unique)")
    
    mode_choice = IntPrompt.ask("[cyan]Choose mode[/cyan]", choices=["1", "2", "3"], default="1")
    
    # Download options
    download = Confirm.ask("\n[cyan]Download songs from YouTube?[/cyan]", default=False)
    format_choice = 'mp3'
    quality = '192'
    download_dir = 'downloads'
    no_metadata = False
    
    if download:
        console.print("\n[cyan]Download format:[/cyan]")
        console.print("1. MP3 (audio only)")
        console.print("2. M4A (audio only, better quality)")
        console.print("3. MP4 (video)")
        format_num = IntPrompt.ask("[cyan]Choose format[/cyan]", choices=["1", "2", "3"], default="1")
        format_choice = ['mp3', 'm4a', 'mp4'][format_num - 1]
        
        if format_choice in ['mp3', 'm4a']:
            console.print("\n[cyan]Audio quality:[/cyan]")
            console.print("1. 128 kbps (smaller files)")
            console.print("2. 192 kbps (balanced)")
            console.print("3. 320 kbps (best quality)")
            console.print("4. Best available")
            quality_num = IntPrompt.ask("[cyan]Choose quality[/cyan]", choices=["1", "2", "3", "4"], default="2")
            quality = ['128', '192', '320', 'best'][quality_num - 1]
        
        download_dir = Prompt.ask("[cyan]Download directory[/cyan]", default="downloads")
        no_metadata = not Confirm.ask("[cyan]Add ID3 metadata tags?[/cyan]", default=True)
    
    return {
        'channel': channel,
        'pages': pages,
        'max_songs': max_songs,
        'output': output,
        'unique_only': mode_choice == "2",
        'save_both': mode_choice == "3",
        'quiet': False,
        'no_color': False,
        'start_id': '',
        'download': download,
        'format': format_choice,
        'quality': quality,
        'download_dir': download_dir,
        'no_metadata': no_metadata,
    }


def display_summary(all_data: List[Dict], unique_data: List[Dict], 
                   saved_files: List[tuple], pages_scraped: int, channel: str):
    """Display a summary table of the scraping results"""
    table = Table(title=f"Scraping Summary - {channel.upper()}", show_header=True, header_style="bold magenta")
    
    table.add_column("Metric", style="cyan", width=25)
    table.add_column("Value", style="green", justify="right")
    
    table.add_row("Channel", channel.upper())
    table.add_row("Pages Scraped", str(pages_scraped))
    table.add_row("Total Songs Found", str(len(all_data)))
    table.add_row("Unique Songs", str(len(unique_data)))
    table.add_row("Duplicates Removed", str(len(all_data) - len(unique_data)))
    
    if saved_files:
        table.add_section()
        for filename, count in saved_files:
            table.add_row(f"Saved: {filename}", f"{count} songs")
    
    console.print()
    console.print(table)
    
    # Show sample tracks
    if unique_data:
        console.print("\n[bold cyan]Sample Tracks:[/bold cyan]")
        sample_table = Table(show_header=True, header_style="bold yellow")
        sample_table.add_column("Time", style="dim")
        sample_table.add_column("Artist", style="cyan")
        sample_table.add_column("Song", style="green")
        sample_table.add_column("YouTube ID", style="blue")
        
        for track in unique_data[:5]:
            sample_table.add_row(
                track['timestamp'],
                track['artist'][:30],
                track['song'][:30],
                track['youtube_id']
            )
        
        console.print(sample_table)


def main():
    """Main function to scrape playlist with CLI support"""
    args = parse_arguments()
    
    # Handle list-channels command
    if args.list_channels:
        list_channels()
        sys.exit(0)
    
    # Validate channel
    channel = args.channel.lower()
    if not validate_channel(channel):
        console.print(f"[yellow]⚠ Warning: '{channel}' not in known channels list.[/yellow]")
        console.print("[yellow]Will attempt to scrape anyway. Use --list-channels to see all channels.[/yellow]\n")
    
    # Handle no-color mode
    if args.no_color:
        console.no_color = True
    
    # Interactive mode
    if args.interactive or (len(sys.argv) == 1):
        config = get_interactive_config()
        channel = config['channel']
        args.pages = config['pages']
        args.max_songs = config['max_songs']
        args.output = config['output']
        args.unique_only = config['unique_only']
        args.save_both = config['save_both']
        args.quiet = config['quiet']
        args.start_id = config['start_id']
        args.download = config.get('download', False)
        args.format = config.get('format', 'mp3')
        args.quality = config.get('quality', '192')
        args.download_dir = config.get('download_dir', 'downloads')
        args.no_metadata = config.get('no_metadata', False)
    
    # Handle batch download from CSV
    if args.from_csv:
        console.print(f"[cyan]Loading songs from {args.from_csv}...[/cyan]")
        all_data = load_songs_from_csv(args.from_csv)
        
        if not all_data:
            console.print("[red]No songs loaded from CSV![/red]")
            sys.exit(1)
        
        console.print(f"[green]✓ Loaded {len(all_data)} songs from CSV[/green]")
        
        # Filter unique if requested
        if args.unique_only:
            unique_data = filter_unique_songs(all_data)
            console.print(f"[cyan]Filtered to {len(unique_data)} unique songs[/cyan]")
            songs_to_download = unique_data
        else:
            songs_to_download = all_data
        
        # Download if requested
        if args.download:
            download_dir = Path(args.download_dir)
            
            console.print(f"\n[cyan]Downloading {len(songs_to_download)} songs to {download_dir}/[/cyan]")
            
            successful = 0
            failed = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Downloading...", 
                    total=len(songs_to_download)
                )
                
                for song in songs_to_download:
                    success, msg = download_youtube_audio(
                        youtube_id=song.get('youtube_id', ''),
                        artist=song.get('artist', ''),
                        song=song.get('song', ''),
                        channel=song.get('channel', channel),
                        download_dir=download_dir,
                        format_choice=args.format,
                        quality=args.quality,
                        add_metadata=not args.no_metadata,
                        progress=progress,
                        task_id=task
                    )
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                        if not args.quiet:
                            console.print(f"[yellow]{msg}[/yellow]")
            
            # Show download summary
            console.print(f"\n[green]✓ Download complete: {successful} successful, {failed} failed[/green]")
        
        sys.exit(0)
    
    # Set default output filename if not specified
    if not args.output:
        args.output = f"{channel}_playlist.csv"
    
    all_data = []
    pages_scraped = 0
    
    # Create session and get initial cookies
    session = requests.Session()
    
    if not args.quiet:
        console.print(f"[cyan]Scraping {channel.upper()} playlist...[/cyan]")
        console.print("[cyan]Initializing session and getting cookies...[/cyan]")
    
    try:
        response = session.get(
            f"https://myonlineradio.de/{channel}/playlist",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30,
        )
        if response.status_code == 200:
            if not args.quiet:
                console.print("[green]✓ Session initialized[/green]")
        elif response.status_code == 404:
            console.print(f"[red]✗ Error: Channel '{channel}' not found![/red]")
            console.print("[yellow]Use --list-channels to see available channels.[/yellow]")
            sys.exit(1)
        time.sleep(2)
    except Exception as e:
        console.print(f"[yellow]⚠ Warning: Could not get cookies: {e}[/yellow]")
    
    # Start scraping with progress bar
    if args.quiet:
        # Quiet mode - no progress bar
        last_id = args.start_id
        for page in range(1, args.pages + 1):
            if args.max_songs and len(all_data) >= args.max_songs:
                break
            
            page_data = scrape_playlist(session, channel=channel, act_page=page, last_id=last_id)
            if not page_data:
                break
            
            all_data.extend(page_data)
            pages_scraped = page
            
            if page_data:
                last_id = page_data[-1]["data_id"]
            
            if page < args.pages:
                time.sleep(1)
    else:
        # Rich progress bar mode
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Scraping {channel.upper()} pages...", total=args.pages)
            
            last_id = args.start_id
            for page in range(1, args.pages + 1):
                # Check if we've hit the song limit
                if args.max_songs and len(all_data) >= args.max_songs:
                    progress.update(task, description=f"[yellow]✓ Reached max songs limit ({args.max_songs})")
                    break
                
                page_data = scrape_playlist(session, channel=channel, act_page=page, last_id=last_id, 
                                           progress=progress, task_id=task)
                if not page_data:
                    progress.update(task, description=f"[yellow]✓ No more data at page {page}")
                    break
                
                all_data.extend(page_data)
                pages_scraped = page
                
                # Update last_id for next page
                if page_data:
                    last_id = page_data[-1]["data_id"]
                
                # Rate limiting
                if page < args.pages and (not args.max_songs or len(all_data) < args.max_songs):
                    time.sleep(1)
            
            progress.update(task, completed=pages_scraped)
    
    # Trim to max_songs if specified
    if args.max_songs and len(all_data) > args.max_songs:
        all_data = all_data[:args.max_songs]
    
    # Filter unique songs
    unique_data = filter_unique_songs(all_data)
    
    # Save files based on mode
    saved_files = []
    
    if args.save_both:
        # Save both all and unique
        all_filename = args.output.replace('.csv', '_all.csv') if '.csv' in args.output else f"{args.output}_all.csv"
        unique_filename = args.output.replace('.csv', '_unique.csv') if '.csv' in args.output else f"{args.output}_unique.csv"
        
        if save_to_csv(all_data, all_filename):
            saved_files.append((all_filename, len(all_data)))
            console.print(f"[green]✓ Saved all songs to {all_filename}[/green]")
        
        if save_to_csv(unique_data, unique_filename):
            saved_files.append((unique_filename, len(unique_data)))
            console.print(f"[green]✓ Saved unique songs to {unique_filename}[/green]")
    
    elif args.unique_only:
        # Save only unique
        if save_to_csv(unique_data, args.output):
            saved_files.append((args.output, len(unique_data)))
            console.print(f"[green]✓ Saved unique songs to {args.output}[/green]")
    
    else:
        # Save all (default)
        if save_to_csv(all_data, args.output):
            saved_files.append((args.output, len(all_data)))
            console.print(f"[green]✓ Saved all songs to {args.output}[/green]")
    
    # Download songs if requested (live mode)
    if args.download and not args.from_csv:
        # Determine which songs to download
        if args.unique_only or args.save_both:
            songs_to_download = unique_data
        else:
            songs_to_download = all_data
        
        download_dir = Path(args.download_dir)
        console.print(f"\n[cyan]Downloading {len(songs_to_download)} songs to {download_dir}/[/cyan]")
        
        successful = 0
        failed = 0
        
        if args.quiet:
            # Quiet mode - no progress bar
            for song in songs_to_download:
                success, msg = download_youtube_audio(
                    youtube_id=song.get('youtube_id', ''),
                    artist=song.get('artist', ''),
                    song=song.get('song', ''),
                    channel=channel,
                    download_dir=download_dir,
                    format_choice=args.format,
                    quality=args.quality,
                    add_metadata=not args.no_metadata
                )
                
                if success:
                    successful += 1
                else:
                    failed += 1
        else:
            # Progress bar mode
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Downloading {args.format.upper()}...", 
                    total=len(songs_to_download)
                )
                
                for song in songs_to_download:
                    success, msg = download_youtube_audio(
                        youtube_id=song.get('youtube_id', ''),
                        artist=song.get('artist', ''),
                        song=song.get('song', ''),
                        channel=channel,
                        download_dir=download_dir,
                        format_choice=args.format,
                        quality=args.quality,
                        add_metadata=not args.no_metadata,
                        progress=progress,
                        task_id=task
                    )
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                        console.print(f"[yellow]{msg}[/yellow]")
        
        console.print(f"\n[green]✓ Download complete: {successful} successful, {failed} failed[/green]")
    
    # Display summary
    if not args.quiet:
        display_summary(all_data, unique_data, saved_files, pages_scraped, channel)


if __name__ == "__main__":
    main()
