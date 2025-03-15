# 硅基流动参考音色上传工具

## 简介

这是一个用于上传参考音频创建自定义音色的工具，适用于硅基流动API。通过简单的界面操作，您可以轻松上传音频文件，创建专属于您的AI语音音色。
[硅基流动文档](https://docs.siliconflow.cn/cn/userguide/capabilities/text-to-speech#5)


## 功能特点

- 简洁直观的用户界面
- 支持多种音频格式上传
- 支持选择不同的模型
- 自动验证API密钥
- 提供详细的上传结果信息
- 支持桌面应用和网页两种使用方式

## 安装方法

### 方法一：直接下载可执行文件（构建exe没成功,不折腾了 请用方法二）

1. 从[发布页面](https://github.com/flyhunterl/SiliconflowVoiceUpLoad/releases)下载最新版本的可执行文件
2. 解压缩下载的文件
3. 双击运行`voice_upload_tool.exe`

### 方法二：从源码安装(有python环境的直接运行start_app.bat就行)

#### 前提条件

- Python 3.7+
- Node.js（可选，用于桌面应用）

#### 安装步骤

1. 克隆或下载本仓库
   ```
   git clone https://github.com/flyhunterl/SiliconflowVoiceUpLoad.git
   cd SiliconflowVoiceUpLoad
   ```

2. 安装Python依赖
   ```
   pip install -r requirements.txt
   ```

3. 运行程序
   ```
   python voice_upload_tool_gradio.py
   ```

## 使用方法

1. 启动应用后，您将看到一个简洁的界面
2. 输入您的API Key（从[硅基流动控制台](https://cloud.siliconflow.cn/account/ak)获取）
3. 上传参考音频文件（支持mp3、wav等格式）
4. 选择模型名称
5. 为您的音色取一个名字
6. 输入音频中说的文字内容（尽量准确匹配音频内容）
7. 点击"提交上传"按钮
8. 上传成功后，您将获得一个音色ID，可用于后续请求

## 注意事项

- **重要：使用自定义音色功能需要完成实名认证**
- 音频文件应清晰无噪音，时长建议在5-30秒之间
- 文字内容应与音频内容精确匹配，这将影响克隆音色的质量
- 上传过程可能需要一些时间，请耐心等待

## 常见问题

### Q: 为什么上传失败？
A: 请检查以下几点：
- API Key是否正确
- 网络连接是否正常
- 音频文件是否符合要求
- 是否已完成实名认证

### Q: 如何获取API Key？
A: 登录[硅基流动控制台](https://cloud.siliconflow.cn/account/ak)，在API密钥管理页面获取。

### Q: 支持哪些音频格式？
A: 支持常见的音频格式，如mp3、wav、ogg等。

## 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个Pull Request

## 打赏

如果您觉得这个项目对您有帮助，欢迎打赏支持作者继续维护和开发更多功能！

![20250314_125818_133_copy](https://github.com/user-attachments/assets/33df0129-c322-4b14-8c41-9dc78618e220)

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 联系方式

- 作者博客：[https://llingfei.com](https://llingfei.com)
- 问题反馈：请在[GitHub Issues](https://github.com/flyhunterl/SiliconflowVoiceUpLoad/issues)提交

