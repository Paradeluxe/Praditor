#!/usr/bin/env python3
"""
PyInstaller打包脚本，用于构建Praditor应用

使用方法：
1. 安装依赖：pip install -r requirements.txt
2. 运行打包：python scripts/build.py
3. 可选参数：
   - python scripts/build.py --onefile  # 单文件模式
   - python scripts/build.py --debug    # 调试模式
   - python scripts/build.py --clean    # 清理之前的构建
   - python scripts/build.py --console  # 控制台输出模式
"""

import os
import sys
import subprocess
import argparse
import shutil
import requests
import re


# 项目根目录
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 入口文件路径
MAIN_ENTRY_FILE = os.path.join(ROOT_DIR, 'src', 'app', 'main.py')
# 默认入口文件
ENTRY_FILE = MAIN_ENTRY_FILE

# 输出目录
OUTPUT_DIR = os.path.join(ROOT_DIR, 'dist')
BUILD_DIR = os.path.join(ROOT_DIR, 'build')

# 资源文件配置
RESOURCES = [
    # 图标文件
    (os.path.join(ROOT_DIR, 'resources', 'icons'), 'resources/icons'),
    # 配置文件
    (os.path.join(ROOT_DIR, 'src', 'app'), 'src/app'),
]

# 命令行参数解析
parser = argparse.ArgumentParser(description='Build Praditor with PyInstaller')
parser.add_argument('--onefile', action='store_true', help='Build as a single executable file')
parser.add_argument('--debug', action='store_true', help='Build in debug mode')
parser.add_argument('--clean', action='store_true', help='Clean previous builds before building')
parser.add_argument('--version', type=str, help='Specify the application version (e.g., 1.3.1 or 1.3.4b)')
parser.add_argument('--new', action='store_true', help='Increment the latest version number to create a new version')
parser.add_argument('--console', action='store_true', help='Build with console output instead of windowed mode')
parser.add_argument('--windowed', action='store_true', help='Build in windowed mode (no console) instead of console mode')
args = parser.parse_args()

def get_latest_github_version():
    """从GitHub获取最新版本号"""
    url = "https://github.com/Paradeluxe/Praditor/releases"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 使用正则表达式匹配版本号，格式为 vX.Y.Z 或 vX.Y.Zb 等
        version_pattern = r'Version\s+(v?\d+\.\d+\.\d+[a-zA-Z]*)'
        matches = re.findall(version_pattern, response.text)
        
        if matches:
            # 提取最新版本号（第一个匹配项）
            latest_version = matches[0]
            # 确保版本号以v开头
            if not latest_version.startswith('v'):
                latest_version = f'v{latest_version}'
            return latest_version
        else:
            print("Warning: Could not find version pattern in GitHub releases")
            return None
    except Exception as e:
        print(f"Warning: Failed to get latest version from GitHub: {e}")
        return None

def increment_version(version):
    """递增版本号，规则：
    - 去除v前缀
    - 分割主版本号、次版本号、修订号
    - 修订号加1
    - 如果有后缀（如b、rc等），保留后缀
    """
    # 去除v前缀
    version = version.lstrip('v')
    
    # 分离版本号和后缀
    version_parts = re.match(r'(\d+)\.(\d+)\.(\d+)([a-zA-Z]*)', version)
    if not version_parts:
        print(f"Warning: Invalid version format: {version}")
        return version
    
    major = int(version_parts.group(1))
    minor = int(version_parts.group(2))
    patch = int(version_parts.group(3))
    suffix = version_parts.group(4)
    
    # 递增修订号
    patch += 1
    
    # 重新组合版本号
    new_version = f'v{major}.{minor}.{patch}{suffix}'
    return new_version

# 如果用户指定了版本号，则使用用户输入的版本号
if args.version:
    # 确保版本号以v开头
    if not args.version.startswith('v'):
        APP_VERSION = f'v{args.version}'
    else:
        APP_VERSION = args.version
else:
    # 从GitHub获取最新版本号
    latest_version = get_latest_github_version()
    if latest_version:
        if args.new:
            # 如果提供了--new参数，则递增版本号
            APP_VERSION = increment_version(latest_version)
            print(f"Auto-incrementing version from GitHub latest {latest_version} to {APP_VERSION}")
        else:
            # 默认使用最新版本号
            APP_VERSION = latest_version
            print(f"Using latest GitHub version: {APP_VERSION}")
    else:
        # 如果无法获取GitHub版本号，使用默认版本
        APP_VERSION = "v1.0.0"
        print(f"Could not get GitHub version, using default: {APP_VERSION}")


# 检测当前操作系统
def get_os_suffix():
    """获取操作系统后缀"""
    if sys.platform.startswith('win'):
        return '_win'
    elif sys.platform.startswith('darwin'):
        return '_mac'
    else:
        return ''

# 设置应用名称
OS_SUFFIX = get_os_suffix()
APP_NAME = f'Praditor_{APP_VERSION}{OS_SUFFIX}'



def clean_build():
    """清理之前的构建文件"""
    print("Cleaning previous builds...")
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    # 清理根目录下的所有.spec文件
    for file in os.listdir(ROOT_DIR):
        if file.endswith('.spec'):
            spec_file = os.path.join(ROOT_DIR, file)
            os.remove(spec_file)
            print(f"Removed {spec_file}")
    
    # 清理scripts目录下的所有.spec文件
    scripts_dir = os.path.join(ROOT_DIR, 'scripts')
    for file in os.listdir(scripts_dir):
        if file.endswith('.spec'):
            spec_file = os.path.join(scripts_dir, file)
            os.remove(spec_file)
            print(f"Removed {spec_file}")


def build():
    """执行PyInstaller打包"""
    # 清理之前的构建（如果需要）
    if args.clean:
        clean_build()
    
    # 构建PyInstaller命令
    # 指定spec文件输出目录为scripts文件夹
    SPEC_DIR = os.path.join(ROOT_DIR, 'scripts')
    cmd = [
        'pyinstaller',
        f'--name={APP_NAME}',
        f'--icon={os.path.join(ROOT_DIR, "resources", "icons", "icon.ico")}',
        f'--distpath={OUTPUT_DIR}',
        f'--workpath={BUILD_DIR}',
        f'--specpath={SPEC_DIR}',
    ]
    
    # 窗口模式或控制台模式
    if args.windowed or not args.console:
        cmd.append('--windowed')  # 无控制台窗口
    
    # 单文件模式
    if args.onefile:
        cmd.append('--onefile')
    
    # 调试模式
    if args.debug:
        cmd.append('--debug=all')
    
    # 添加资源文件
    for src, dst in RESOURCES:
        cmd.append(f'--add-data={src}{os.pathsep}{dst}')
    
    # 添加入口文件
    cmd.append(ENTRY_FILE)
    
    print(f"Building Praditor with command: {' '.join(cmd)}")
    
    # 执行打包命令
    result = subprocess.run(cmd, cwd=ROOT_DIR, check=False)
    
    if result.returncode == 0:
        print(f"\nBuild completed successfully!")
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"\nYou can find the executable in: {OUTPUT_DIR}")
    else:
        print(f"\nBuild failed with return code: {result.returncode}")
        sys.exit(1)


if __name__ == '__main__':
    build()
