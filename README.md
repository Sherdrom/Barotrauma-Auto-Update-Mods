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

### 4. 运行脚本

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
4. **下载更新**: 使用 SteamCMD 的 `workshop_download_item` 命令下载/更新模组

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

确保 SteamCMD 已正确安装并在 PATH 中，或者修改 `main.py` 中的 `steamcmd_path` 变量指向正确的路径。

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
