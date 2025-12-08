# Barotrauma 模组自动更新工具

自动从 Steam 创意工坊下载和更新 Barotrauma 游戏的模组。

## 功能

- 自动解析 `config_player.xml` 配置文件
- 提取所有模组的 Steam 创意工坊ID
- 自动下载缺失的模组
- 自动更新已有模组
- 使用 SteamCMD 进行下载，保证下载的模组是最新版本

## 使用方法

### 1. 安装依赖

确保系统已安装 Python 3.6+。

### 2. 安装 SteamCMD

**Windows:**
- 从 [SteamCMD 官方页面](https://developer.valvesoftware.com/wiki/SteamCMD) 下载 SteamCMD
- 将 steamcmd.exe 放在项目目录下，或添加到系统 PATH

**macOS:**
```bash
brew install steamcmd
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install steamcmd

# 或手动下载
wget https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz
tar -xzf steamcmd_linux.tar.gz
```

### 3. 准备配置文件

将您的 `config_player.xml` 文件（位于 Barotrauma 配置目录下）复制到项目目录。

### 4. 配置脚本（可选）

脚本使用 `config.json` 文件进行配置。如果不存在，会自动创建默认配置。

**默认配置文件内容:**
```json
{
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
```

**自定义 SteamCMD 路径:**
编辑 `config.json` 文件，修改 `steamcmd.path` 为您的 SteamCMD 实际路径：

**Windows 示例:**
```json
{
  "steamcmd": {
    "path": "C:\\Program Files (x86)\\Steam\\steamcmd.exe"
  }
}
```

**macOS 示例:**
```json
{
  "steamcmd": {
    "path": "/opt/homebrew/bin/steamcmd"
  }
}
```

**Linux 示例:**
```json
{
  "steamcmd": {
    "path": "/usr/bin/steamcmd"
  }
}
```

### 5. 运行脚本

```bash
python main.py
```

## 输出说明

脚本会显示以下信息：
- 解析到的模组数量
- 检查更新状态
- 每个模组的下载进度
- 最终统计结果

示例输出：
```
=== Barotrauma 模组自动更新工具 ===

正在解析配置文件: config_player.xml
找到 66 个模组

检查模组更新状态...
发现 5 个模组需要更新或下载

正在下载模组 2559634234...
✓ 模组 2559634234 下载成功

正在下载模组 2795927223...
✓ 模组 2795927223 下载成功

...

=== 下载完成 ===
成功: 5
失败: 0
```

## 工作原理

1. **解析配置**: 使用 XML 解析读取 `config_player.xml` 文件
2. **提取ID**: 正则表达式匹配 `LocalMods/{ID}/filelist.xml` 格式的路径
3. **检查更新**: 检查 LocalMods 目录下的模组是否存在 filelist.xml
4. **下载更新**: 使用 SteamCMD 的 `workshop_download_item` 命令下载模组到 `LocalMods/steamapps/workshop/content/274900/{ID}/`
5. **整理文件**: 将下载的文件移动到 `LocalMods/{ID}/` 目录，清理临时文件

## 目录结构说明

下载过程会产生以下目录结构：

```
LocalMods/
├── 2559634234/          # Barotrauma 期望的最终位置
│   ├── filelist.xml
│   └── ...
└── steamapps/           # SteamCMD 临时目录（下载完成后会清理）
    └── workshop/
        └── content/
            └── 274900/
                └── 2559634234/  # SteamCMD 实际下载位置
                    ├── filelist.xml
                    └── ...
```

脚本会自动将文件从临时目录移动到最终位置，并清理 `steamapps` 目录。

## 目录结构

下载的模组会保存在 `LocalMods/` 目录下，每个模组一个子目录：

```
LocalMods/
├── 2559634234/          # 模组ID
│   ├── filelist.xml
│   └── ...
├── 2795927223/
│   ├── filelist.xml
│   └── ...
└── ...
```

## 故障排除

### 找不到 steamcmd

1. **检查配置文件**: 打开 `config.json` 文件，确认 `steamcmd.path` 设置正确
2. **添加到 PATH**: 将 SteamCMD 添加到系统 PATH 中，然后使用 `"path": "steamcmd"`
3. **使用绝对路径**: 直接在配置文件中设置 SteamCMD 的完整路径

### 模组下载后不在 LocalMods 目录

**已修复**: 脚本会自动处理 SteamCMD 的下载路径。下载的文件会从 `LocalMods/steamapps/workshop/content/274900/{mod_id}/` 自动移动到 `LocalMods/{mod_id}/`，并清理临时目录。

如果遇到问题：
1. 检查脚本输出中是否有移动文件的提示
2. 确认对当前目录有写权限
3. 查看是否有错误信息

### 下载失败

- 检查网络连接
- 确认 Steam 账户可访问创意工坊内容
- 检查防火墙设置
- 查看详细错误信息

### 权限错误

确保对当前目录有写入权限，脚本需要创建 `LocalMods/` 目录。

## 注意事项

- 首次运行会下载所有模组，需要较长时间
- 后续运行只会下载更新的模组
- 脚本使用 `anonymous` 账户登录，依赖 Steam 的公开访问权限
- 下载超时设置为 5 分钟每个模组，可根据网络情况调整
