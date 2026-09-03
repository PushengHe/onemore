# coding: utf-8
"""
自动打包并创建 GitHub Release 的辅助脚本
使用方法: python release.py <版本号>
例如: python release.py 2.0.6
"""
import os
import sys
import shutil
import zipfile
from pathlib import Path
import subprocess

def get_version():
    """从命令行参数获取版本号"""
    if len(sys.argv) < 2:
        print("使用方法: python release.py <版本号>")
        print("例如: python release.py 2.0.6")
        sys.exit(1)
    return sys.argv[1]

def update_version_in_code(version):
    """更新代码中的版本号"""
    setting_file = Path("app/common/setting.py")
    if not setting_file.exists():
        print(f"错误: 找不到 {setting_file}")
        return False
    
    content = setting_file.read_text(encoding='utf-8')
    
    # 查找并替换版本号
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('VERSION ='):
            old_version = line
            lines[i] = f'VERSION = "v{version}"'
            print(f"版本号已更新: {old_version} -> {lines[i]}")
            break
    
    setting_file.write_text('\n'.join(lines), encoding='utf-8')
    return True

def build_executable():
    """使用 Nuitka 打包可执行文件"""
    print("\n" + "="*60)
    print("开始打包可执行文件...")
    print("="*60)
    
    result = subprocess.run(['python', 'deploy.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print("打包失败:")
        print(result.stderr)
        return False
    
    print("打包成功!")
    return True

def create_zip_package(version):
    """创建 ZIP 发布包"""
    print("\n" + "="*60)
    print("创建 ZIP 发布包...")
    print("="*60)
    
    dist_dir = Path("build/main.dist")
    if not dist_dir.exists():
        print(f"错误: 找不到打包目录 {dist_dir}")
        return None
    
    # 创建 release 目录
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    
    # ZIP 文件名
    zip_filename = f"OneMore-v{version}-Windows-x64.zip"
    zip_path = release_dir / zip_filename
    
    # 删除旧的 zip 文件
    if zip_path.exists():
        zip_path.unlink()
    
    print(f"正在压缩: {dist_dir} -> {zip_path}")
    
    # 创建 ZIP 文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, arcname)
                print(f"  添加: {arcname}")
    
    print(f"ZIP 包创建成功: {zip_path}")
    print(f"文件大小: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return zip_path

def create_release_notes(version):
    """生成发布说明"""
    notes = f"""# OneMore v{version}

## 🎉 新增功能

- [在这里添加新功能说明]

## 🐛 修复问题

- [在这里添加修复的问题]

## ⚡ 性能优化

- [在这里添加性能优化说明]

## 📝 其他更新

- [在这里添加其他更新]

---

## 📦 安装方法

1. 下载 `OneMore-v{version}-Windows-x64.zip`
2. 解压到任意目录
3. 运行 `main.exe` 启动程序

## 🔄 升级方法

- 如果已安装旧版本，可以直接在软件内点击"检查更新"进行在线更新
- 或者手动下载后覆盖旧版本文件

## ⚠️ 注意事项

- 需要 Windows 10/11 系统
- 首次运行可能需要管理员权限
"""
    
    notes_file = Path("release") / f"release-notes-v{version}.md"
    notes_file.write_text(notes, encoding='utf-8')
    print(f"\n发布说明模板已创建: {notes_file}")
    print("请编辑此文件，然后手动创建 GitHub Release")
    
    return notes_file

def print_github_release_instructions(version, zip_path, notes_file):
    """打印 GitHub Release 创建说明"""
    print("\n" + "="*60)
    print("GitHub Release 创建说明")
    print("="*60)
    
    print(f"""
1. 前往 GitHub 仓库: https://github.com/PushengHe/onemore/releases/new

2. 填写 Release 信息:
   - Tag: v{version}
   - Title: OneMore v{version}
   - Description: 复制 {notes_file} 的内容

3. 上传文件:
   - {zip_path}

4. 发布:
   - 如果是正式版本，取消勾选 "This is a pre-release"
   - 点击 "Publish release"

5. 或使用 GitHub CLI (如果已安装):
   gh release create v{version} \\
       --title "OneMore v{version}" \\
       --notes-file {notes_file} \\
       {zip_path}
""")

def main():
    print("="*60)
    print("OneMore 发布包构建工具")
    print("="*60)
    
    # 获取版本号
    version = get_version()
    print(f"\n目标版本: v{version}")
    
    # 确认
    response = input("\n是否继续? (y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return
    
    # 步骤1: 更新版本号
    print("\n[1/5] 更新代码中的版本号...")
    if not update_version_in_code(version):
        print("更新版本号失败")
        return
    
    # 步骤2: 打包可执行文件
    print("\n[2/5] 打包可执行文件...")
    if not build_executable():
        print("打包失败")
        return
    
    # 步骤3: 创建 ZIP 包
    print("\n[3/5] 创建 ZIP 发布包...")
    zip_path = create_zip_package(version)
    if not zip_path:
        print("创建 ZIP 包失败")
        return
    
    # 步骤4: 创建发布说明
    print("\n[4/5] 生成发布说明...")
    notes_file = create_release_notes(version)
    
    # 步骤5: 打印后续步骤
    print("\n[5/5] 准备发布到 GitHub...")
    print_github_release_instructions(version, zip_path, notes_file)
    
    print("\n" + "="*60)
    print("✅ 发布包构建完成!")
    print("="*60)
    print(f"\n发布包位置: {zip_path.absolute()}")
    print(f"发布说明: {notes_file.absolute()}")
    print("\n请按照上述说明创建 GitHub Release")

if __name__ == '__main__':
    main()
