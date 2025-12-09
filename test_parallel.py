#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试并行下载功能的脚本
"""

from main import load_config, download_mods_parallel, check_mod_updates
import json

def test_config():
    """测试配置加载"""
    print("=== 测试配置加载 ===")
    config, config_path = load_config()

    print(f"配置文件路径: {config_path}")
    print(f"配置内容:")
    print(json.dumps(config, indent=2, ensure_ascii=False))

    # 检查必需的配置项
    required_keys = ['steamcmd', 'files', 'download']
    for key in required_keys:
        if key in config:
            print(f"✓ {key} 配置存在")
        else:
            print(f"✗ {key} 配置缺失")

    # 检查 max_workers
    if 'download' in config and 'max_workers' in config['download']:
        max_workers = config['download']['max_workers']
        print(f"✓ 并行下载进程数: {max_workers}")
        if max_workers < 1 or max_workers > 10:
            print(f"⚠️  警告: max_workers={max_workers} 可能不合适，建议 1-10")
    else:
        print("✗ max_workers 配置缺失，将使用默认值 3")

    print()

def test_parallel_download():
    """测试并行下载（仅显示信息，不实际下载）"""
    print("=== 测试并行下载函数 ===")
    config, _ = load_config()
    workshop_path = config['files']['workshop_path']
    steamcmd_path = config['steamcmd']['path']
    timeout = config['download']['timeout']
    max_workers = config['download']['max_workers']

    print(f"SteamCMD 路径: {steamcmd_path}")
    print(f"模组目录: {workshop_path}")
    print(f"超时时间: {timeout} 秒")
    print(f"并发数: {max_workers}")
    print()

    # 模拟下载列表
    test_mod_ids = ['1234567890', '1234567891', '1234567892']
    print(f"模拟下载模组: {test_mod_ids}")
    print(f"如果运行实际下载，将使用 {max_workers} 个进程并行下载")
    print()

def main():
    """主测试函数"""
    print("=" * 60)
    print("Barotrauma 模组更新工具 - 并行下载功能测试")
    print("=" * 60)
    print()

    test_config()
    test_parallel_download()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    print()
    print("要运行实际的模组更新，请执行:")
    print("  python main.py")

if __name__ == "__main__":
    main()
