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
"""

import os
import sys
import subprocess
import argparse
import shutil

# 项目根目录
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 入口文件路径
MAIN_ENTRY_FILE = os.path.join(ROOT_DIR, 'src', 'app', 'main.py')
AUTO_ENTRY_FILE = os.path.join(ROOT_DIR, 'src', 'app', 'auto_main.py')
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
    (os.path.join(ROOT_DIR, 'config'), 'config'),
]

# 命令行参数解析
parser = argparse.ArgumentParser(description='Build Praditor with PyInstaller')
parser.add_argument('--onefile', action='store_true', help='Build as a single executable file')
parser.add_argument('--debug', action='store_true', help='Build in debug mode')
parser.add_argument('--clean', action='store_true', help='Clean previous builds before building')
parser.add_argument('--auto', action='store_true', help='Build the auto-VAD version instead of the main version')
args = parser.parse_args()

# 根据参数选择入口文件
if args.auto:
    ENTRY_FILE = AUTO_ENTRY_FILE
    APP_NAME = 'AutoPraditor'
else:
    ENTRY_FILE = MAIN_ENTRY_FILE
    APP_NAME = 'Praditor'


def clean_build():
    """清理之前的构建文件"""
    print("Cleaning previous builds...")
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    spec_file = os.path.join(ROOT_DIR, 'scripts', 'build.spec')
    if os.path.exists(spec_file):
        os.remove(spec_file)


def build():
    """执行PyInstaller打包"""
    # 清理之前的构建（如果需要）
    if args.clean:
        clean_build()
    
    # 构建PyInstaller命令
    cmd = [
        'pyinstaller',
        f'--name={APP_NAME}',
        '--windowed',  # 无控制台窗口
        f'--icon={os.path.join(ROOT_DIR, "resources", "icons", "icon.ico")}',
        f'--distpath={OUTPUT_DIR}',
        f'--workpath={BUILD_DIR}',
    ]
    
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
        
        # 复制README和LICENSE到输出目录
        for file in ['README.md', 'README_zh.md', 'LICENSE']:
            src = os.path.join(ROOT_DIR, file)
            dst = os.path.join(OUTPUT_DIR, file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"Copied {file} to output directory")
        
        print(f"\nYou can find the executable in: {OUTPUT_DIR}")
    else:
        print(f"\nBuild failed with return code: {result.returncode}")
        sys.exit(1)


if __name__ == '__main__':
    build()
