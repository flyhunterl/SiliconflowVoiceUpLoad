import gradio as gr
import requests
import os
import tempfile
import logging
import sys
import subprocess
import threading
import webbrowser
from pathlib import Path

# 禁用代理设置
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_voice(api_key, audio_file, model_name, voice_name, voice_text):
    """
    上传音频文件创建自定义参考音色
    
    参数:
        api_key (str): 硅基流动API密钥
        audio_file (str): 音频文件路径
        model_name (str): 模型名称
        voice_name (str): 参考音频名称
        voice_text (str): 参考音频文字内容
        
    返回:
        str: 上传结果信息
    """
    # 参数验证
    if not api_key:
        return "错误：请输入API Key"
    if not audio_file:
        return "错误：请上传音频文件"
    if not voice_name:
        return "错误：请输入参考音频名称"
    if not voice_text:
        return "错误：请输入参考音频文字内容"
    
    try:
        # 准备API请求
        url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
        headers = {
            "Authorization": f"Bearer {api_key.strip()}"  # 去除可能的空格
        }
        
        # 检查文件是否存在
        if not os.path.exists(audio_file):
            return f"错误：文件不存在 - {audio_file}"
            
        # 检查文件大小
        file_size = os.path.getsize(audio_file) / (1024 * 1024)  # 转换为MB
        if file_size > 50:  # 假设最大限制为50MB
            return f"错误：文件过大 ({file_size:.2f}MB)，请上传小于50MB的文件"
        
        logger.info(f"准备上传文件: {os.path.basename(audio_file)}, 大小: {file_size:.2f}MB")
        
        files = {
            "file": open(audio_file, "rb")
        }
        data = {
            "model": model_name.strip(),
            "customName": voice_name.strip(),
            "text": voice_text.strip()
        }
        
        # 发送请求
        logger.info("发送API请求...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        
        # 显示响应
        if response.status_code == 200:
            result = response.json()
            logger.info(f"上传成功: {result}")
            if "uri" in result:
                return f"上传成功！\n\n音色ID (uri): {result['uri']}\n\n您可以将此ID作为后续请求中的voice参数使用。"
            else:
                return f"上传成功，但未返回uri字段\n\n{result}"
        else:
            logger.error(f"上传失败: {response.status_code} - {response.text}")
            return f"上传失败，状态码: {response.status_code}\n\n{response.text}"
    except requests.exceptions.Timeout:
        logger.error("请求超时")
        return "错误：请求超时，请稍后重试"
    except requests.exceptions.ConnectionError:
        logger.error("连接错误")
        return "错误：无法连接到服务器，请检查网络连接"
    except Exception as e:
        logger.exception("上传过程中发生错误")
        return f"发生错误: {str(e)}"
    finally:
        # 确保文件被关闭
        if 'files' in locals() and 'file' in files:
            files['file'].close()

def validate_api_key(api_key):
    """验证API密钥格式"""
    if not api_key:
        return "请输入API Key"
    if len(api_key.strip()) < 10:  # 假设API Key至少有10个字符
        return "API Key格式可能不正确"
    return None

def create_electron_files():
    """创建Electron应用所需的文件"""
    # 创建package.json
    package_json = {
        "name": "voice-upload-tool",
        "version": "1.0.0",
        "description": "硅基流动参考音色上传工具",
        "main": "main.js",
        "scripts": {
            "start": "electron ."
        },
        "dependencies": {
            "electron": "^28.0.0"
        }
    }
    
    # 创建main.js，添加隐藏菜单栏的代码
    main_js = """
const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const url = require('url');

let mainWindow;

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      nodeIntegration: true
    },
    title: '硅基流动参考音色上传工具'
  });

  // 隐藏菜单栏
  Menu.setApplicationMenu(null);

  // 加载应用
  mainWindow.loadURL('http://127.0.0.1:7860/');
  
  // 打开开发者工具
  // mainWindow.webContents.openDevTools();

  // 当窗口关闭时触发
  mainWindow.on('closed', function () {
    mainWindow = null;
    // 关闭Python服务器
    process.exit();
  });
}

// 当Electron完成初始化并准备创建浏览器窗口时调用此方法
app.on('ready', createWindow);

// 当所有窗口关闭时退出应用
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});
"""
    
    # 创建electron目录
    electron_dir = Path("electron_app")
    electron_dir.mkdir(exist_ok=True)
    
    # 写入文件
    with open(electron_dir / "package.json", "w", encoding="utf-8") as f:
        import json
        json.dump(package_json, f, indent=2)
    
    with open(electron_dir / "main.js", "w", encoding="utf-8") as f:
        f.write(main_js)
    
    logger.info("Electron文件创建完成")
    return electron_dir

def find_npm():
    """尝试在常见的安装位置查找npm"""
    # 检查是否已在PATH中
    try:
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "npm"  # npm在PATH中可用
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # 常见的Node.js安装路径
    common_paths = [
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        r"C:\ProgramData\nodejs\npm.cmd",
        os.path.expanduser("~\\AppData\\Roaming\\npm\\npm.cmd"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Node.js\npm.cmd"
    ]
    
    # 检查Node.js安装目录
    nodejs_dir = os.environ.get("ProgramFiles") + "\\nodejs"
    if os.path.exists(nodejs_dir):
        common_paths.append(os.path.join(nodejs_dir, "npm.cmd"))
    
    # 尝试在注册表中查找Node.js安装路径
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Node.js")
        value, _ = winreg.QueryValueEx(key, "InstallPath")
        if value:
            common_paths.append(os.path.join(value, "npm.cmd"))
    except:
        pass
    
    # 检查每个可能的路径
    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"找到npm: {path}")
            return path
    
    return None

def launch_electron_app(electron_dir):
    """启动Electron应用"""
    try:
        # 查找npm
        npm_cmd = find_npm()
        if not npm_cmd:
            raise FileNotFoundError("未找到npm命令")
        
        # 检查electron_app目录中是否已安装依赖
        node_modules_path = electron_dir / "node_modules"
        if not node_modules_path.exists():
            # 安装依赖
            logger.info("安装Electron依赖...")
            if npm_cmd == "npm":
                # npm在PATH中可用
                subprocess.run(["npm", "install"], cwd=electron_dir, check=True)
            else:
                # 使用完整路径
                subprocess.run([npm_cmd, "install"], cwd=electron_dir, check=True)
        
        # 启动Electron应用
        logger.info("启动Electron应用...")
        if npm_cmd == "npm":
            subprocess.Popen(["npm", "start"], cwd=electron_dir)
        else:
            subprocess.Popen([npm_cmd, "start"], cwd=electron_dir)
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"未安装npm或安装依赖失败: {e}")
        logger.error("将使用浏览器打开应用")
        webbrowser.open("http://127.0.0.1:7860/")
        return False
    except Exception as e:
        logger.exception(f"启动Electron应用失败: {e}")
        webbrowser.open("http://127.0.0.1:7860/")
        return False

# 创建Gradio界面
def create_gradio_interface():
    # 定义颜色变量
    primary_color = "#6366f1"  # 紫色
    light_bg_color = "#f3f4f6"  # 浅灰色背景
    
    # 自定义主题
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="gray"
    ).set(
        button_primary_background_fill=primary_color,
        button_primary_background_fill_hover="#4f46e5",  # 深一点的紫色
        block_title_background_fill=light_bg_color,
        block_label_background_fill=light_bg_color,
        input_background_fill="white",
        background_fill_primary="white"
    )
    
    with gr.Blocks(title="硅基流动自定义参考音色上传工具", theme=theme) as demo:
        # 标题栏 - 使用与按钮相同的背景色
        with gr.Row():
            gr.Markdown(f'<div style="background-color: {primary_color}; color: white; padding: 15px; border-radius: 8px; text-align: center; width: 100%; margin-bottom: 20px;"><h1 style="margin: 0; font-size: 24px;">硅基流动参考音色上传工具</h1></div>')
        
        # 主要内容区域
        with gr.Row():
            # 左侧区域 - 音频上传、文字内容和API Key
            with gr.Column(scale=1):
                # 音频上传区域
                with gr.Group(elem_id="audio-upload-group"):
                    gr.Markdown(f'<div style="background-color: {light_bg_color}; padding: 8px; border-radius: 5px;"><h3 style="margin: 0;">音频</h3></div>')
                    audio_file = gr.Audio(
                        label="", 
                        type="filepath",
                        format="mp3",
                        elem_id="audio-upload"
                    )
                    
                    with gr.Row():
                        gr.Button("⬆️", size="sm")
                        gr.Button("🎤", size="sm")
                
                # 参考音频文字内容（移到这里）
                with gr.Group(elem_id="voice-text-group"):
                    gr.Markdown(f'<div style="background-color: {light_bg_color}; padding: 8px; border-radius: 5px;"><h3 style="margin: 0;">参考音频文字内容</h3></div>')
                    voice_text = gr.Textbox(
                        label="", 
                        placeholder="请输入音频中说的文字内容", 
                        lines=3,
                        elem_id="voice-text-input"
                    )
                
                # API Key输入
                with gr.Group(elem_id="api-key-group"):
                    gr.Markdown(f'<div style="background-color: {light_bg_color}; padding: 8px; border-radius: 5px;"><h3 style="margin: 0;">API Key</h3></div>')
                    api_key = gr.Textbox(
                        label="", 
                        placeholder="请输入您的API Key（不需要输入Bearer前缀）", 
                        type="password",
                        elem_id="api-key-input"
                    )
            
            # 右侧区域 - 模型名称和参考音频名称
            with gr.Column(scale=1):
                # 模型选择
                with gr.Group(elem_id="model-group"):
                    gr.Markdown(f'<div style="background-color: {light_bg_color}; padding: 8px; border-radius: 5px;"><h3 style="margin: 0;">模型名称</h3></div>')
                    model_name = gr.Textbox(
                        label="",
                        value="FunAudioLLM/CosyVoice2-0.5B",
                        elem_id="model-input"
                    )
                
                # 参考音频名称
                with gr.Group(elem_id="voice-name-group"):
                    gr.Markdown(f'<div style="background-color: {light_bg_color}; padding: 8px; border-radius: 5px;"><h3 style="margin: 0;">参考音频名称</h3></div>')
                    voice_name = gr.Textbox(
                        label="", 
                        placeholder="请为您的音色取一个名字",
                        elem_id="voice-name-input"
                    )
        
        # 提交按钮和结果显示移到最下方
        with gr.Row():
            with gr.Column(scale=1):
                submit_btn = gr.Button("提交上传", variant="primary", size="lg", elem_id="submit-button")
            
        with gr.Row():
            with gr.Column():
                # 结果显示区域
                with gr.Group(elem_id="result-group"):
                    gr.Markdown(f'<div style="background-color: {light_bg_color}; padding: 8px; border-radius: 5px;"><h3 style="margin: 0;">结果</h3></div>')
                    output = gr.Textbox(
                        label="", 
                        lines=5,
                        elem_id="result-output"
                    )
        
        # 添加API Key验证
        api_key.change(
            fn=validate_api_key,
            inputs=api_key,
            outputs=gr.Textbox(visible=False)
        )
        
        # 提交按钮事件
        submit_btn.click(
            fn=upload_voice,
            inputs=[api_key, audio_file, model_name, voice_name, voice_text],
            outputs=output
        )
        
        # 使用说明
        with gr.Accordion("使用说明", open=False, elem_id="instructions-accordion"):
            gr.Markdown("""
            1. 输入您的API Key（从 [https://cloud.siliconflow.cn/account/ak](https://cloud.siliconflow.cn/account/ak) 获取）
            2. 上传参考音频文件（支持常见音频格式，如mp3、wav等）
            3. 选择模型名称
            4. 为您的音色取一个名字
            5. 输入音频中说的文字内容（尽量准确匹配音频内容）
            6. 点击"提交上传"按钮
            7. 上传成功后，您将获得一个音色ID，可用于后续请求
            
            **重要提示：使用自定义音色功能需要完成实名认证**
            
            **注意事项**：
            - 音频文件应清晰无噪音，时长建议在5-30秒之间
            - 文字内容应与音频内容精确匹配，这将影响克隆音色的质量
            """)
        
        # 页脚
        with gr.Row(elem_id="footer"):
            with gr.Column(scale=3):
                gr.Markdown("© 2024 硅基流动 | 参考音色上传工具")
            with gr.Column(scale=1):
                gr.Markdown("<div style='text-align: right;'><a href='https://llingfei.com' target='_blank'>作者博客: https://llingfei.com</a></div>")
        
        # 添加自定义CSS
        gr.HTML("""
        <style>
            .gradio-container {
                max-width: 1200px !important;
                margin-left: auto !important;
                margin-right: auto !important;
            }
            
            /* 统一背景颜色 */
            .gradio-group {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-bottom: 15px;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            /* 美化标题 */
            h3 {
                font-weight: 600;
                color: #4b5563;
            }
            
            /* 美化按钮 */
            #submit-button {
                width: 100%;
                margin-top: 10px;
                font-weight: bold;
            }
            
            /* 美化输入框 */
            input, textarea, select {
                border: 1px solid #d1d5db !important;
                border-radius: 5px !important;
            }
            
            /* 页脚样式 */
            #footer {
                margin-top: 20px;
                padding-top: 10px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
            }
        </style>
        """)
    
    return demo

def is_packaged():
    """检查是否是打包后的环境"""
    return getattr(sys, 'frozen', False)

def get_resource_path(relative_path):
    """获取资源文件路径，兼容开发环境和打包环境"""
    if is_packaged():
        # 如果是打包后的环境，使用 sys._MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def setup_logging():
    """配置日志系统"""
    try:
        if is_packaged():
            # 打包环境下将日志写入临时目录
            log_dir = os.path.join(tempfile.gettempdir(), "voice_upload_tool")
        else:
            # 开发环境下写入当前目录的 logs 文件夹
            log_dir = "logs"
        
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "voice_upload.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        logger.info("日志系统初始化成功")
    except Exception as e:
        print(f"设置日志系统时出错: {e}")

if __name__ == "__main__":
    try:
        # 设置日志
        setup_logging()
        
        # 创建 Gradio 界面
        demo = create_gradio_interface()
        
        # 启动 Gradio 服务器
        logger.info("启动 Gradio 服务器...")
        # 兼容旧版本Gradio
        try:
            demo.queue(concurrency_count=1)  # 新版Gradio
        except TypeError:
            demo.queue()  # 旧版Gradio
            
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            show_api=False,
            share=False,
            inbrowser=True
        )
    except Exception as e:
        logger.exception("程序运行出错")
        # 在打包环境下，保持窗口打开以显示错误信息
        if is_packaged():
            input("程序运行出错，按回车键退出...")