# 桌面便签工具

这是一个功能丰富的桌面便签工具，可以帮助你快速记录和管理日常笔记。

## 主要功能

### 1. 文本编辑
- 支持富文本编辑（加粗、斜体、下划线）
- 可自定义字体样式和大小
- 支持文字颜色设置
- 支持文本对齐方式调整（左对齐、居中、右对齐）

### 2. 界面特性
- 窗口透明度可调（使用"日"和"月"按钮）
- 支持窗口拖动和大小调整
- 窗口置顶显示
- 可最小化到系统托盘

### 3. 搜索功能
- 支持文本内容搜索
- 向下继续搜索
- 集成Google搜索
- 内容筛选功能

### 4. 自动保存
- 每10秒自动保存内容
- 每天16:00定时保存
- 程序启动时自动加载上次内容

### 5. 快捷按钮
- 提供20个可自定义的快捷按钮
- 通过buttons.json配置文件自定义按钮功能
- 支持：
  - 打开文件或程序
  - 运行自定义命令
  - 执行特定操作

### 6. 其他功能
- 自动识别和高亮超链接
- 右键菜单快捷操作
- 帮助文档查看

## 使用说明

### 基本操作
1. 启动程序后，可以直接在文本框中输入内容
2. 使用格式工具栏调整文本样式
3. 通过右上角按钮调整窗口透明度
4. 可以拖动窗口到任意位置

### 快捷按钮配置
1. 点击"m"按钮打开配置文件
2. 在buttons.json中设置按钮功能：
   - id：按钮编号（1-20）
   - name：按钮显示名称
   - function：功能类型（open_file/run_command/custom_action）
   - params：功能参数

### 搜索使用
1. 在底部搜索框输入关键词
2. 使用不同搜索按钮：
   - 文本：在当前内容中搜索
   - 向下：继续查找下一个
   - google：使用Google搜索
   - 筛选：筛选显示匹配内容

## 注意事项
- 程序会自动保存内容，无需手动保存
- 可以通过系统托盘图标右键菜单退出程序
- 建议定期备份buttons.json配置文件

## 系统要求
- 操作系统：Windows
- 需要安装Python环境和相关依赖包

## 技术支持
如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件至开发者邮箱

## 许可证
本软件遵循MIT许可证。