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
from pathlib import Path


def load_config(config_path="config.json"):
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        dict: 配置字典，如果文件不存在则返回默认配置
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

    if not os.path.exists(config_path):
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return default_config

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
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        print("使用默认配置")
        return default_config


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
        "+workshop_download_item", "602960", mod_id,
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
            # 将下载的文件移动到最终位置
            if steamcmd_download_path.exists():
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

            print(f"✓ 模组 {mod_id} 下载成功")
            return True
        else:
            print(f"✗ 模组 {mod_id} 下载失败")
            print(f"错误信息: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ 模组 {mod_id} 下载超时")
        return False
    except Exception as e:
        print(f"✗ 下载模组 {mod_id} 时出错: {e}")
        return False


def check_mod_updates(mod_ids, workshop_path, config_file_path):
    """
    检查模组更新

    基于以下规则判断：
    1. 模组目录不存在 → 需要下载
    2. filelist.xml 不存在 → 需要下载
    3. 模组目录的修改时间早于配置文件 → 需要更新
    4. filelist.xml 的修改时间早于配置文件 → 需要更新

    Args:
        mod_ids: 模组ID列表
        workshop_path: 创意工坊内容路径
        config_file_path: Barotrauma 配置文件路径

    Returns:
        list: 需要更新的模组ID列表
    """
    needs_update = []
    workshop = Path(workshop_path)
    config_file = Path(config_file_path)

    # 获取配置文件的修改时间
    config_mtime = config_file.stat().st_mtime if config_file.exists() else 0

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

        # 检查3: 比较修改时间
        mod_mtime = mod_path.stat().st_mtime
        filelist_mtime = filelist_path.stat().st_mtime

        # 如果配置文件比模组目录或 filelist.xml 更新，说明模组需要更新
        if config_mtime > mod_mtime or config_mtime > filelist_mtime:
            print(f"  模组 {mod_id}: 配置已更新，需要重新下载")
            needs_update.append(mod_id)
        else:
            print(f"  模组 {mod_id}: 已是最新")

    return needs_update


def main():
    """主函数"""
    # 加载配置
    print("=== Barotrauma 模组自动更新工具 ===\n")
    config = load_config()

    # 从配置中获取设置
    config_file = config["files"]["config_file"]
    workshop_path = config["files"]["workshop_path"]
    steamcmd_path = config["steamcmd"]["path"]
    timeout = config["download"]["timeout"]

    # 将相对路径转换为绝对路径（重要！）
    workshop_path = str(Path(workshop_path).resolve())

    print(f"使用配置文件: config.json")
    print(f"SteamCMD 路径: {steamcmd_path}")
    print(f"模组下载目录: {workshop_path}")
    print(f"下载超时: {timeout} 秒\n")

    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f"错误: 找不到配置文件 {config_file}")
        sys.exit(1)

    # 解析配置文件
    print(f"正在解析配置文件: {config_file}")
    mod_ids = parse_config_for_mod_ids(config_file)

    if not mod_ids:
        print("未找到任何模组配置")
        sys.exit(0)

    print(f"找到 {len(mod_ids)} 个模组\n")

    # 检查需要更新的模组
    print("检查模组更新状态...")
    update_list = check_mod_updates(mod_ids, workshop_path, config_file)

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
