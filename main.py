#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Barotrauma 模组自动更新工具
自动从 Steam 创意工坊下载和更新模组
"""

import xml.etree.ElementTree as ET
import subprocess
import os
import re
import sys
import json
import shutil
import requests
from pathlib import Path


def load_config(config_path="config.json"):
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        tuple: (配置字典, 配置文件绝对路径)
    """
    default_config = {
        "steamcmd": {
            "path": "steamcmd"
        },
        "files": {
            "config_file": "config_player.xml",
            "workshop_path": "LocalMods"
        },
        "download": {
            "timeout": 300
        }
    }

    # 获取配置文件的绝对路径
    config_path = Path(config_path).resolve()

    if not config_path.exists():
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return default_config, config_path

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # 合并默认配置（防止缺失键）
        for section in default_config:
            if section not in config:
                config[section] = default_config[section]
            elif isinstance(default_config[section], dict):
                for key in default_config[section]:
                    if key not in config[section]:
                        config[section][key] = default_config[section][key]
        return config, config_path
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        print("使用默认配置")
        return default_config, config_path


def parse_config_for_mod_ids(config_path):
    """
    解析配置文件，提取所有模组ID

    Args:
        config_path: 配置文件路径

    Returns:
        list: 模组ID列表
    """
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()

        # 查找所有 package 元素
        mod_ids = []
        for package in root.findall('.//package'):
            path = package.get('path', '')
            # 提取 LocalMods/ID/filelist.xml 中的 ID
            match = re.search(r'LocalMods/(\d+)/filelist\.xml', path)
            if match:
                mod_ids.append(match.group(1))

        return mod_ids
    except Exception as e:
        print(f"解析配置文件时出错: {e}")
        return []


def download_mod_steamcmd(mod_id, workshop_path, steamcmd_path="steamcmd", timeout=300):
    """
    使用 SteamCMD 下载模组

    Args:
        mod_id: Steam 创意工坊模组ID
        workshop_path: 创意工坊内容路径（绝对路径）
        steamcmd_path: SteamCMD 可执行文件路径
        timeout: 下载超时时间（秒）

    Returns:
        bool: 下载是否成功
    """
    workshop = Path(workshop_path)
    workshop.mkdir(parents=True, exist_ok=True)

    # SteamCMD 会下载到: workshop/steamapps/workshop/content/602960/{mod_id}/
    # 我们需要将内容移动到: workshop/{mod_id}/
    steamcmd_download_path = workshop / "steamapps" / "workshop" / "content" / "602960" / mod_id
    final_mod_path = workshop / mod_id

    # SteamCMD 下载命令
    cmd = [
        steamcmd_path,
        "+force_install_dir", str(workshop),
        "+login", "anonymous",
        "+workshop_download_item", "602960", mod_id, "validate",
        "+quit"
    ]

    try:
        print(f"正在下载模组 {mod_id}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            # 验证下载是否成功
            # 检查下载目录是否存在
            if not steamcmd_download_path.exists():
                print(f"✗ 模组 {mod_id} 下载失败: SteamCMD 未能创建下载目录")
                print(f"SteamCMD 输出: {result.stdout}")
                print(f"SteamCMD 错误: {result.stderr}")
                return False

            # 检查下载目录是否为空
            downloaded_files = list(steamcmd_download_path.iterdir())
            if not downloaded_files:
                print(f"✗ 模组 {mod_id} 下载失败: SteamCMD 未下载任何文件到预期位置")
                print(f"SteamCMD 输出: {result.stdout}")
                print(f"SteamCMD 错误: {result.stderr}")
                return False

            # 检查 filelist.xml 是否存在（这是模组的关键文件）
            filelist_path = steamcmd_download_path / "filelist.xml"
            if not filelist_path.exists():
                print(f"✗ 模组 {mod_id} 下载失败: filelist.xml 不存在")
                print(f"下载目录内容: {[f.name for f in downloaded_files]}")
                print(f"SteamCMD 输出: {result.stdout}")
                print(f"SteamCMD 错误: {result.stderr}")
                return False

            # 检查 filelist.xml 是否为空
            if filelist_path.stat().st_size == 0:
                print(f"✗ 模组 {mod_id} 下载失败: filelist.xml 为空文件")
                print(f"SteamCMD 输出: {result.stdout}")
                print(f"SteamCMD 错误: {result.stderr}")
                return False

            # 将下载的文件移动到最终位置
            try:
                # 创建最终目录
                final_mod_path.mkdir(parents=True, exist_ok=True)

                # 移动所有文件
                for item in steamcmd_download_path.iterdir():
                    dest = final_mod_path / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    item.rename(dest)

                # 验证文件是否成功移动
                final_filelist = final_mod_path / "filelist.xml"
                if not final_filelist.exists():
                    print(f"✗ 模组 {mod_id} 文件移动失败: 最终位置未找到 filelist.xml")
                    return False

                print(f"✓ 模组 {mod_id} 下载并移动成功")
                return True
            except Exception as e:
                print(f"✗ 模组 {mod_id} 文件移动时出错: {e}")
                return False
        else:
            print(f"✗ 模组 {mod_id} 下载失败")
            print(f"SteamCMD 错误信息: {result.stderr}")
            print(f"SteamCMD 输出: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ 模组 {mod_id} 下载超时")
        return False
    except Exception as e:
        print(f"✗ 下载模组 {mod_id} 时出错: {e}")
        return False


def get_workshop_update_time(mod_id, timeout=30):
    """
    获取 Steam 创意工坊中模组的更新时间

    使用 Steam Web API: https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/

    Args:
        mod_id: Steam 创意工坊模组ID
        timeout: 查询超时时间（秒）

    Returns:
        float: 模组的更新时间戳（Unix 时间戳），如果获取失败返回 0
    """
    api_url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"

    data = {
        "itemcount": "1",
        "publishedfileids[0]": mod_id
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        result = requests.post(api_url, data=data, headers=headers, timeout=timeout)

        if result.status_code == 200:
            data = result.json()
            if 'response' in data and 'publishedfiledetails' in data['response']:
                publishedfiledetails = data['response']['publishedfiledetails']
                if publishedfiledetails:
                    moddetails = publishedfiledetails[0]
                    if 'time_updated' in moddetails:
                        return float(moddetails['time_updated'])
                    elif 'time_created' in moddetails:
                        return float(moddetails['time_created'])
    except Exception as e:
        print(f"    获取模组 {mod_id} 更新信息失败: {e}")

    return 0


def check_mod_updates(mod_ids, workshop_path):
    """
    检查模组更新

    基于以下规则判断：
    1. 模组目录不存在 → 需要下载
    2. filelist.xml 不存在 → 需要更新
    3. 本地 filelist.xml 修改时间早于 Steam 创意工坊更新时间 → 需要更新

    Args:
        mod_ids: 模组ID列表
        workshop_path: 创意工坊内容路径

    Returns:
        list: 需要更新的模组ID列表
    """
    needs_update = []
    workshop = Path(workshop_path)

    for mod_id in mod_ids:
        mod_path = workshop / mod_id
        filelist_path = mod_path / "filelist.xml"

        # 检查1: 模组目录是否存在
        if not mod_path.exists():
            print(f"  模组 {mod_id}: 目录不存在，需要下载")
            needs_update.append(mod_id)
            continue

        # 检查2: filelist.xml 是否存在
        if not filelist_path.exists():
            print(f"  模组 {mod_id}: filelist.xml 不存在，需要更新")
            needs_update.append(mod_id)
            continue

        # 检查3: 获取 Steam 创意工坊的模组更新时间
        remote_update_time = get_workshop_update_time(mod_id)
        if remote_update_time == 0:
            # 无法获取远程更新时间，跳过检查
            print(f"  模组 {mod_id}: 无法获取更新信息，跳过检查")
            continue

        # 检查4: 比较本地和远程更新时间
        local_mtime = filelist_path.stat().st_mtime

        if remote_update_time > local_mtime:
            print(f"  模组 {mod_id}: Steam 有更新，需要下载")
            needs_update.append(mod_id)
        else:
            print(f"  模组 {mod_id}: 已是最新")

    return needs_update


def main():
    """主函数"""
    # 加载配置
    print("=== Barotrauma 模组自动更新工具 ===\n")
    config, config_path = load_config()

    # 从配置中获取设置
    config_file = config["files"]["config_file"]
    workshop_path = config["files"]["workshop_path"]
    steamcmd_path = config["steamcmd"]["path"]
    timeout = config["download"]["timeout"]

    # 以配置文件所在目录为基准解析相对路径
    config_dir = config_path.parent
    if not Path(workshop_path).is_absolute():
        # 相对路径：相对于配置文件的位置
        workshop_path = str((config_dir / workshop_path).resolve())
    else:
        # 绝对路径：直接使用
        workshop_path = str(Path(workshop_path).resolve())

    print(f"使用配置文件: {config_path}")
    print(f"SteamCMD 路径: {steamcmd_path}")
    print(f"模组下载目录: {workshop_path}")
    print(f"下载超时: {timeout} 秒\n")

    # 检查配置文件是否存在
    config_file_path = Path(config_file)
    if not config_file_path.is_absolute():
        config_file_path = config_dir / config_file
    config_file_path = config_file_path.resolve()

    if not config_file_path.exists():
        print(f"错误: 找不到配置文件 {config_file_path}")
        sys.exit(1)

    # 解析配置文件
    print(f"正在解析配置文件: {config_file_path}")
    mod_ids = parse_config_for_mod_ids(str(config_file_path))

    if not mod_ids:
        print("未找到任何模组配置")
        sys.exit(0)

    print(f"找到 {len(mod_ids)} 个模组\n")

    # 检查需要更新的模组
    print("检查模组更新状态...")
    update_list = check_mod_updates(mod_ids, workshop_path)

    if update_list:
        print(f"发现 {len(update_list)} 个模组需要更新或下载\n")
    else:
        print("所有模组都是最新的\n")

    # 下载/更新模组
    success_count = 0
    fail_count = 0

    for mod_id in update_list:
        if download_mod_steamcmd(mod_id, workshop_path, steamcmd_path, timeout):
            success_count += 1
        else:
            fail_count += 1
        print()  # 空行分隔

    # 汇总结果
    print("=== 下载完成 ===")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")

    # 清理临时目录
    steamapps_dir = Path(workshop_path) / "steamapps"
    if steamapps_dir.exists():
        print("\n正在清理临时文件...")
        shutil.rmtree(steamapps_dir, ignore_errors=True)
        print("✓ 临时文件清理完成")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
