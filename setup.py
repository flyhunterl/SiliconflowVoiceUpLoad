import subprocess
import sys
import os
import webbrowser
from pathlib import Path

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
            print(f"找到npm: {path}")
            return path
    
    return None

def install_dependencies():
    """安装所需的Python依赖"""
    print("正在安装Python依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio", "requests"])
        print("Python依赖安装完成！")
    except subprocess.CalledProcessError:
        print("安装Python依赖失败，请手动运行: pip install gradio requests")
        return False
    
    # 查找npm
    npm_cmd = find_npm()
    npm_installed = npm_cmd is not None
    
    if npm_installed:
        print(f"检测到npm已安装: {npm_cmd}")
    else:
        print("\n未检测到npm。如果您想使用桌面应用功能，请安装Node.js：")
        print("1. 访问 https://nodejs.org/")
        print("2. 下载并安装最新的LTS版本")
        print("3. 安装完成后重新运行此脚本")
        
        # 询问是否打开Node.js下载页面
        answer = input("\n是否打开Node.js下载页面？(y/n): ")
        if answer.lower() == 'y':
            webbrowser.open("https://nodejs.org/")
    
    # 创建electron_app目录和文件，即使npm未安装
    # 这样用户安装npm后可以直接使用
    electron_dir = Path("electron_app")
    electron_dir.mkdir(exist_ok=True)
    
    # 创建package.json
    package_json = """
{
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
"""
    
    # 创建main.js
    main_js = """
const { app, BrowserWindow } = require('electron');
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
    
    # 写入文件
    with open(electron_dir / "package.json", "w", encoding="utf-8") as f:
        f.write(package_json)
    
    with open(electron_dir / "main.js", "w", encoding="utf-8") as f:
        f.write(main_js)
    
    print("\n已创建Electron应用文件")
    
    # 如果npm已安装，尝试安装Electron依赖
    if npm_installed:
        try:
            print("正在安装Electron依赖...")
            if npm_cmd == "npm":
                # npm在PATH中可用
                subprocess.check_call(["npm", "install"], cwd=electron_dir)
            else:
                # 使用完整路径
                subprocess.check_call([npm_cmd, "install"], cwd=electron_dir)
            print("Electron依赖安装完成！")
        except subprocess.CalledProcessError as e:
            print(f"安装Electron依赖失败: {e}")
            print("请手动运行: cd electron_app && npm install")
            npm_installed = False
    
    # 创建或更新start_app.bat
    with open("start_app.bat", "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("echo 正在启动硅基流动参考音色上传工具...\n")
        f.write("python voice_upload_tool_gradio.py\n")
        f.write("pause\n")  # 添加暂停，以便查看可能的错误信息
    
    print("\n安装完成！")
    print("\n运行方式:")
    print("1. 双击 start_app.bat 文件")
    print("2. 或者运行命令: python voice_upload_tool_gradio.py")
    
    if not npm_installed:
        print("\n注意: 由于未找到npm，应用将在浏览器中打开而不是作为桌面应用运行")
        print("如果您已安装Node.js，请确保将其添加到系统PATH环境变量中")
        print("或者重新安装Node.js并选择'Add to PATH'选项")
    
    # 创建README.md文件
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("""# 硅基流动参考音色上传工具

## 简介
这是一个用于上传参考音频创建自定义音色的工具，适用于硅基流动API。

## 安装步骤

### 1. 安装Python依赖

### 2. 安装Node.js

### 3. 安装Electron依赖

### 4. 运行应用

#### 4.1 双击 start_app.bat 文件
#### 4.2 或者运行命令: python voice_upload_tool_gradio.py

### 5. 创建自定义音色

#### 5.1 访问 http://127.0.0.1:7860/ 创建自定义音色
#### 5.2 使用工具上传参考音频
#### 5.3 等待处理完成

### 6. 使用自定义音色

#### 6.1 在应用中选择自定义音色
#### 6.2 使用自定义音色进行语音合成

## 注意事项

- 确保Node.js已安装并添加到系统PATH环境变量中
- 确保Electron依赖已正确安装
- 如果遇到问题，请检查控制台输出并根据提示进行操作

## 联系我们

如果您有任何问题或建议，请随时联系我们。

### 联系方式

- 邮箱: [your-email@example.com](mailto:your-email@example.com)
- 微信: [your-wechat-id](wechat-id)
- 电话: [your-phone-number](phone-number)

感谢您的使用！""")
    
    return True

if __name__ == "__main__":
    install_dependencies() 