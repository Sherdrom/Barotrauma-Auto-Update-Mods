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
from pathlib import Path


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


def download_mod_steamcmd(mod_id, workshop_path, steamcmd_path="steamcmd"):
    """
    使用 SteamCMD 下载模组

    Args:
        mod_id: Steam 创意工坊模组ID
        workshop_path: 创意工坊内容路径
        steamcmd_path: SteamCMD 可执行文件路径

    Returns:
        bool: 下载是否成功
    """
    mod_path = Path(workshop_path) / mod_id
    mod_path.mkdir(parents=True, exist_ok=True)

    # SteamCMD 下载命令
    cmd = [
        steamcmd_path,
        "+force_install_dir", str(mod_path.parent.parent),
        "+login", "anonymous",
        "+workshop_download_item", "274900", mod_id,
        "+quit"
    ]

    try:
        print(f"正在下载模组 {mod_id}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
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


def check_mod_updates(mod_ids, workshop_path):
    """
    检查模组更新（重新下载即为更新）

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
        if not mod_path.exists() or not (mod_path / "filelist.xml").exists():
            needs_update.append(mod_id)

    return needs_update


def main():
    """主函数"""
    # 配置路径
    config_file = "config_player.xml"
    workshop_path = "LocalMods"
    steamcmd_path = "steamcmd"  # 假设 steamcmd 已在 PATH 中

    print("=== Barotrauma 模组自动更新工具 ===\n")

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
    update_list = check_mod_updates(mod_ids, workshop_path)

    if update_list:
        print(f"发现 {len(update_list)} 个模组需要更新或下载\n")
    else:
        print("所有模组都是最新的\n")

    # 下载/更新模组
    success_count = 0
    fail_count = 0

    for mod_id in update_list:
        if download_mod_steamcmd(mod_id, workshop_path, steamcmd_path):
            success_count += 1
        else:
            fail_count += 1
        print()  # 空行分隔

    # 汇总结果
    print("=== 下载完成 ===")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
