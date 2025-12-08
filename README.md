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
- 检查更新状态（每个模组的详细检查结果）
- 每个模组的下载进度
- 最终统计结果
- 临时文件清理信息

示例输出：
```
=== Barotrauma 模组自动更新工具 ===

正在解析配置文件: config_player.xml
找到 66 个模组

检查模组更新状态...
  模组 2559634234: 已是最新
  模组 2795927223: 目录不存在，需要下载
  模组 2701251094: 配置已更新，需要重新下载
发现 2 个模组需要更新或下载

正在下载模组 2795927223...
✓ 模组 2795927223 下载成功

...

=== 下载完成 ===
成功: 2
失败: 0

正在清理临时文件...
✓ 临时文件清理完成
```

## 工作原理

1. **解析配置**: 使用 XML 解析读取 `config_player.xml` 文件
2. **提取ID**: 正则表达式匹配 `LocalMods/{ID}/filelist.xml` 格式的路径
3. **智能检查更新**: 对每个模组进行多级检查
   - 检查模组目录是否存在
   - 检查 filelist.xml 是否存在
   - 比较文件修改时间（配置文件 vs 模组目录/filelist.xml）
   - 提供详细的检查结果
4. **绝对路径**: 将相对路径转换为绝对路径，确保 SteamCMD 下载到正确位置
5. **下载更新**: 使用 SteamCMD 的 `workshop_download_item` 命令下载模组到 `LocalMods/steamapps/workshop/content/602960/{ID}/`
6. **整理文件**: 将下载的文件移动到 `LocalMods/{ID}/` 目录
7. **清理临时文件**: 所有模组下载完成后，统一清理 `steamapps` 临时目录

## 智能更新检查机制

脚本实现了智能的模组更新检查，避免不必要的重复下载：

### 检查规则

1. **目录存在性检查**
   - 模组目录不存在 → 需要下载
   - 示例: `模组 2559634234: 目录不存在，需要下载`

2. **文件完整性检查**
   - filelist.xml 不存在 → 需要更新
   - 示例: `模组 2559634234: filelist.xml 不存在，需要更新`

3. **时间戳比较检查**
   - 配置文件修改时间 > 模组目录修改时间 → 需要更新
   - 配置文件修改时间 > filelist.xml 修改时间 → 需要更新
   - 示例: `模组 2559634234: 配置已更新，需要重新下载`
   - 示例: `模组 2559634234: 已是最新`

### 工作流程

```
开始检查
    ↓
检查模组目录是否存在？
    ├─ 否 → 需要下载
    └─ 是 → 继续检查
        ↓
检查 filelist.xml 是否存在？
        ├─ 否 → 需要更新
        └─ 是 → 继续检查
            ↓
比较配置文件与模组的时间戳
            ├─ 配置文件更新 → 需要更新
            └─ 模组更新 → 已是最新
```

### 优势

- **精确检查**: 只下载真正需要更新的模组
- **节省时间**: 避免不必要的网络传输
- **节省带宽**: 减少 Steam 服务器负载
- **详细反馈**: 显示每个模组的检查结果
- **智能判断**: 基于时间戳的准确判断

## 重要说明：路径处理

⚠️ **为什么需要绝对路径？**

SteamCMD 的 `+force_install_dir` 参数如果使用相对路径，会相对于 SteamCMD 所在目录而不是项目目录。这会导致模组下载到错误的位置。

✅ **脚本自动处理**:
- 自动将配置中的相对路径转换为绝对路径
- 确保下载到项目目录下的 `LocalMods` 文件夹
- 无需用户手动配置绝对路径

## 目录结构说明

下载过程会产生以下目录结构：

```
LocalMods/
├── 2559634234/          # Barotrauma 期望的最终位置
│   ├── filelist.xml
│   └── ...
└── steamapps/           # SteamCMD 临时目录（下载过程中存在）
    └── workshop/
        └── content/
            └── 602960/
                └── 2559634234/  # SteamCMD 实际下载位置
                    ├── filelist.xml
                    └── ...
```

脚本会自动将文件从临时目录移动到最终位置。**所有模组下载完成后，`steamapps` 目录会被完全清理**，最终只保留模组文件。

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

**问题**: 模组下载到了其他位置的 LocalMods 文件夹

**原因**: SteamCMD 使用相对路径时会相对于 SteamCMD 所在目录，而不是项目目录。

**解决方案**: ✅ **已修复** - 脚本现在会自动将相对路径转换为绝对路径，确保下载到项目目录下的 LocalMods 中。

如果仍然遇到问题：
1. 检查脚本输出中的 "模组下载目录" 是否显示为绝对路径
2. 确认对项目目录有写权限
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
