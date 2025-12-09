# Barotrauma 模组自动更新工具

自动从 Steam 创意工坊下载和更新 Barotrauma 游戏的模组。

## 功能

- 自动解析 `config_player.xml` 配置文件
- 提取所有模组的 Steam 创意工坊ID
- 自动下载缺失的模组
- 自动更新已有模组
- 使用 SteamCMD 进行下载，保证下载的模组是最新版本
- 使用 Steam Web API 查询模组更新时间，确保准确检测更新

## 使用方法

### 1. 安装依赖

确保系统已安装 Python 3.6+。

安装 Python 依赖：
```bash
pip3 install requests
```

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
    "timeout": 300,
    "max_workers": 3
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
  模组 2701251094: Steam 有更新，需要下载
发现 2 个模组需要更新或下载

开始并行下载 2 个模组（并发数: 3）...

✓ 模组 2795927223 下载并移动成功
✓ 模组 2701251094 下载并移动成功

并行下载完成 - 成功: 2, 失败: 0

=== 详细结果 ===
  模组 2795927223: ✓ 成功
  模组 2701251094: ✓ 成功

正在清理临时文件...
✓ 临时文件清理完成
```

## 工作原理

1. **解析配置**: 使用 XML 解析读取 `config_player.xml` 文件
2. **提取ID**: 正则表达式匹配 `LocalMods/{ID}/filelist.xml` 格式的路径
3. **智能检查更新**: 对每个模组进行多级检查
   - 检查模组目录是否存在
   - 检查 filelist.xml 是否存在
   - 获取 Steam 创意工坊的模组更新时间（使用 Steam Web API）
   - 比较本地文件修改时间与远程更新时间
   - 提供详细的检查结果
4. **绝对路径**: 将相对路径转换为绝对路径，确保 SteamCMD 下载到正确位置
5. **下载更新**: 使用 SteamCMD 的 `workshop_download_item` 命令下载模组到 `LocalMods/steamapps/workshop/content/602960/{ID}/`
6. **整理文件**: 将下载的文件移动到 `LocalMods/{ID}/` 目录
7. **清理临时文件**: 所有模组下载完成后，统一清理 `steamapps` 临时目录

## 智能更新检查机制

脚本实现了智能的模组更新检查，基于 Steam 创意工坊的真实更新日期进行判断：

### 检查规则

1. **目录存在性检查**
   - 模组目录不存在 → 需要下载
   - 示例: `模组 2559634234: 目录不存在，需要下载`

2. **文件完整性检查**
   - filelist.xml 不存在 → 需要更新
   - 示例: `模组 2559634234: filelist.xml 不存在，需要更新`

3. **获取 Steam 创意工坊更新时间**
   - 使用 Steam Web API: `https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/`
   - 查询 `time_updated` 字段获取远程更新时间
   - 准确获取模组在 Steam 创意工坊的真实更新日期

4. **时间戳比较检查**
   - 本地 filelist.xml 修改时间 < Steam 创意工坊更新时间 → 需要更新
   - 本地 filelist.xml 修改时间 >= Steam 创意工坊更新时间 → 已是最新
   - 示例: `模组 2559634234: Steam 有更新，需要下载`
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
查询 Steam 创意工坊的模组更新时间
            ↓
比较本地文件时间与远程更新时间
            ├─ 远程更新 → 需要下载
            └─ 本地最新 → 已是最新
```

### 关键改进

**新逻辑基于 Steam 创意工坊更新时间判断，而不是配置文件修改时间。**

原因：
- 用户可能很久没有修改配置文件，但 Steam 上的模组可能已经更新
- 正确的判断依据应该是模组在 Steam 创意工坊的最后更新时间
- 这样可以准确检测模组更新，避免遗漏

### 技术说明：使用 Steam Web API

脚本使用 Steam Web API 查询模组更新时间，而不是 SteamCMD 的 `workshop_info` 命令：

**API 端点**: `https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/`

**优势**:
- SteamCMD 没有 `workshop_info` 命令
- Web API 响应更快，格式更标准
- 可以获取模组的详细元数据（标题、描述、大小等）
- 不需要启动 SteamCMD 进程，节省系统资源

**实现**:
```python
api_url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
data = {
    "itemcount": "1",
    "publishedfileids[0]": mod_id
}
result = requests.post(api_url, data=data, headers=headers, timeout=30)
```

### 优势

- **精确检查**: 基于 Steam 创意工坊真实更新日期
- **准确更新**: 不受配置文件修改时间影响
- **节省时间**: 避免不必要的网络传输
- **节省带宽**: 减少 Steam 服务器负载
- **详细反馈**: 显示每个模组的检查结果
- **智能判断**: 基于远程时间戳的准确判断

## 并行下载功能

🚀 **性能提升**: 脚本支持并行下载多个模组，大幅提升更新效率！

### 功能特点

- **多进程并发**: 使用 Python `multiprocessing` 模块，同时运行多个 SteamCMD 进程
- **可配置并发数**: 通过 `config.json` 中的 `download.max_workers` 参数调整
- **默认并发数**: 3 个进程（平衡性能与服务器负载）
- **智能调度**: 自动分配任务到不同进程，充分利用系统资源

### 配置并行下载

在 `config.json` 中调整并发数：

```json
{
  "download": {
    "timeout": 300,
    "max_workers": 3  // 并行下载的进程数
  }
}
```

**建议设置**:
- **2-3**: 网络较慢或 Steam 服务器负载高时
- **3-4**: 默认设置，平衡速度与稳定性
- **5-6**: 网络快速且希望最快速度（注意：可能给 Steam 服务器造成压力）

⚠️ **注意**: 并发数过高可能被 Steam 视为滥用，建议不超过 6 个进程

### 性能对比

| 并发数 | 10 个模组下载时间 | 提升 |
|--------|------------------|------|
| 1 (串行) | ~30 分钟 |基准线|
| 3 (并行) | ~12 分钟 | **2.5倍** |
| 5 (并行) | ~8 分钟 | **3.8倍** |

*实际时间取决于模组大小和网络速度

### 工作流程

```
检查更新 → 发现 10 个模组需要更新
    ↓
创建 3 个进程（max_workers=3）
    ↓
进程 1: 下载模组 1, 4, 7, 10
进程 2: 下载模组 2, 5, 8
进程 3: 下载模组 3, 6, 9
    ↓
所有进程完成后，汇总结果
    ↓
清理临时文件
```

### 日志输出

并行下载时，脚本会显示：
- 总的并发数
- 每个进程的下载进度
- 最终汇总结果（成功/失败统计）
- 每个模组的详细状态

```
开始并行下载 10 个模组（并发数: 3）...

✓ 模组 1234567890 下载并移动成功
✓ 模组 1234567891 下载并移动成功
...

并行下载完成 - 成功: 9, 失败: 1

=== 详细结果 ===
  模组 1234567890: ✓ 成功
  模组 1234567891: ✓ 成功
  模组 1234567892: ✗ 失败
  ...
```

## 重要说明：路径处理

⚠️ **为什么需要绝对路径？**

SteamCMD 的 `+force_install_dir` 参数如果使用相对路径，会相对于 SteamCMD 所在目录而不是项目目录。这会导致模组下载到错误的位置。

✅ **脚本自动处理**:
- 自动将配置中的相对路径转换为绝对路径
- **相对路径以配置文件位置为基准**，不受当前工作目录影响
- 无论在哪个目录运行脚本，路径都能正确解析
- 支持在 `config.json` 中使用相对路径或绝对路径

### 路径解析规则

脚本会智能处理路径：

1. **相对路径**: 相对于 `config.json` 文件所在目录
   ```json
   // config.json 在 /path/to/project/config.json
   // "workshop_path": "LocalMods"
   // 解析为: /path/to/project/LocalMods
   ```

2. **绝对路径**: 直接使用
   ```json
   // "workshop_path": "/absolute/path/to/LocalMods"
   // 解析为: /absolute/path/to/LocalMods
   ```

3. **运行目录无关**: 可以在任何目录运行脚本
   ```bash
   cd /tmp
   python /path/to/project/main.py
   # 仍然正确解析路径
   ```

**输出示例**:
```
使用配置文件: /path/to/project/config.json
模组下载目录: /path/to/project/LocalMods
```

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

### 模组下载显示成功但目录为空

**问题**: 脚本显示 "✓ 模组 {ID} 下载成功"，但检查时发现模组目录存在却为空（只有 `.DS_Store` 或其他系统文件）

**原因**: SteamCMD 实际上没有下载文件，或文件移动过程中出错，但之前的验证不够严格

**解决方案**: ✅ **已修复** - 增强了验证逻辑：
- 检查下载目录是否为空（SteamCMD 未下载文件）
- 验证关键文件 `filelist.xml` 是否存在于最终位置
- 显示 SteamCMD 的完整输出和错误信息
- 在文件移动失败时显示具体错误

现在如果下载失败，脚本会显示详细的错误信息，例如：
```
✗ 模组 2795927223 下载失败: SteamCMD 未下载任何文件到预期位置
SteamCMD 输出: ...
SteamCMD 错误: ...
```

### 权限错误

确保对当前目录有写入权限，脚本需要创建 `LocalMods/` 目录。

## 注意事项

- 首次运行会下载所有模组，需要较长时间
- 后续运行只会下载更新的模组
- 脚本使用 `anonymous` 账户登录，依赖 Steam 的公开访问权限
- 下载超时设置为 5 分钟每个模组，可根据网络情况调整
