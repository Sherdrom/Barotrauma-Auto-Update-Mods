# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Barotrauma 模组自动更新工具，自动从 Steam 创意工坊下载和更新模组。

The user is a Chinese user, please respond in Chinese.

## How It Works

1. **Parse config**: Reads `config_player.xml` to extract mod IDs from `path="LocalMods/{ID}/filelist.xml"`
2. **Check updates**: Identifies missing or outdated mods in LocalMods directory
3. **Download**: Uses SteamCMD's `workshop_download_item` to download/update mods

## Core Functions

- `parse_config_for_mod_ids(config_path)` - 解析XML提取模组ID
- `check_mod_updates(mod_ids, workshop_path)` - 检查需要更新的模组
- `download_mod_steamcmd(mod_id, workshop_path, steamcmd_path)` - 使用SteamCMD下载模组
- `main()` - 主执行流程

## Development

**Run the tool:**
```bash
python main.py
```

**Test parsing:**
```bash
python3 -c "from main import parse_config_for_mod_ids; print(parse_config_for_mod_ids('config_player.xml'))"
```

**Requirements:**
- Python 3.6+
- SteamCMD installed and in PATH
- config_player.xml in project directory

## Architecture

- Single-file Python script (`main.py`)
- Uses `xml.etree.ElementTree` for XML parsing
- Uses `subprocess` to call SteamCMD
- Downloads to `LocalMods/` directory structure matching game format

## Dependencies

- Python standard library only (no external packages)
- Requires system-installed SteamCMD tool

## Important Files

- `main.py` - Main script with all functionality
- `config_player.xml` - Barotrauma config file containing mod list
- `README.md` - Detailed usage documentation

## Mod ID Format

Steam Workshop mod IDs are extracted from XML paths like:
- `path="LocalMods/2544952900/filelist.xml"` → mod ID: `2544952900`
- Total of 66 mods in example config

