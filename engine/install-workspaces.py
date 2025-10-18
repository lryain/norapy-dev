#!/usr/bin/env python3
"""
OVOS 多包系统的标准解决方案

核心理念：
- 使用"工作区"概念，分层安装
- 核心包优先安装，确保稳定
- 可选地安装扩展包（plugins, skills）
- 使用缓存避免重复解析

这是 Yarn Workspaces/npm Workspaces 风格的解决方案
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple

# Colors
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def log_info(msg):
    print(f"{BLUE}ℹ{NC} {msg}")

def log_success(msg):
    print(f"{GREEN}✓{NC} {msg}")

def log_error(msg):
    print(f"{RED}✗{NC} {msg}")

def log_warn(msg):
    print(f"{YELLOW}⚠{NC} {msg}")

# 定义工作区（手工维护，但清晰可控）
WORKSPACES = {
    'core': {
        'description': '核心系统（必需）',
        'packages': [
            'engine-utils/ovos-utils',
            'engine-core/ovos-config',
            'engine-core/ovos-plugin-manager',
            'engine-core/ovos-workshop',
            'engine-core/ovos-messagebus',
            'engine-core/ovos-core',
        ]
    },
    'gui': {
        'description': 'GUI 相关模块',
        'packages': [
            'engine-core/ovos-gui',
            'engine-core/ovos-shell',
        ]
    },
    'audio': {
        'description': '音频相关模块',
        'packages': [
            'engine-core/ovos-audio',
            'engine-core/ovos-dinkum-listener',
            'engine-core/ovos-PHAL',
        ]
    },
    'clients': {
        'description': '客户端和服务',
        'packages': [
            'engine-clients/ovos-bus-client',
            'engine-servers/ovos-stt-http-server',
            'engine-servers/ovos-tts-server',
        ]
    },
}

# 推荐的默认工作区
DEFAULT_WORKSPACES = ['core']

class WorkspaceManager:
    """工作区管理器"""
    
    def __init__(self, engine_dir: Path):
        self.engine_dir = engine_dir
        self.failed = []
        self.installed = []
    
    def select_workspaces(self, names: List[str] = None) -> List[str]:
        """选择要安装的工作区"""
        if names is None:
            names = DEFAULT_WORKSPACES
        
        selected = []
        for name in names:
            if name in WORKSPACES:
                selected.append(name)
            else:
                log_warn(f"未知的工作区: {name}")
        
        return selected
    
    def get_packages_for_workspaces(self, workspace_names: List[str]) -> List[Tuple[str, Path]]:
        """获取指定工作区的所有包"""
        packages = []
        
        for ws_name in workspace_names:
            if ws_name not in WORKSPACES:
                continue
            
            ws = WORKSPACES[ws_name]
            for pkg_rel_path in ws['packages']:
                pkg_path = self.engine_dir / pkg_rel_path
                
                if pkg_path.exists() and (pkg_path / 'setup.py').exists():
                    # 从 setup.py 中提取包名
                    pkg_name = pkg_path.name
                    packages.append((pkg_name, pkg_path))
                else:
                    log_warn(f"包不存在: {pkg_rel_path}")
        
        return packages
    
    def install_package(self, pkg_name: str, pkg_path: Path) -> bool:
        """安装单个包"""
        try:
            cmd = [
                sys.executable, '-m', 'pip', 'install',
                '--no-build-isolation', '-q',
                '-e', str(pkg_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                log_success(f"已安装: {pkg_name}")
                self.installed.append(pkg_name)
                return True
            else:
                # 尝试不使用 --no-build-isolation
                cmd.remove('--no-build-isolation')
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    log_success(f"已安装: {pkg_name}")
                    self.installed.append(pkg_name)
                    return True
                
                log_error(f"安装失败: {pkg_name}")
                self.failed.append((pkg_name, result.stderr))
                return False
        
        except Exception as e:
            log_error(f"异常: {pkg_name}: {e}")
            self.failed.append((pkg_name, str(e)))
            return False
    
    def install_workspaces(self, workspace_names: List[str]):
        """安装指定的工作区"""
        packages = self.get_packages_for_workspaces(workspace_names)
        
        if not packages:
            log_error("没有找到要安装的包")
            return False
        
        print(f"\n{BLUE}{'='*70}{NC}")
        print(f"{BLUE}安装工作区: {', '.join(workspace_names)}{NC}")
        print(f"{BLUE}总共 {len(packages)} 个包{NC}")
        print(f"{BLUE}{'='*70}{NC}\n")
        
        for i, (pkg_name, pkg_path) in enumerate(packages, 1):
            print(f"[{i}/{len(packages)}] {pkg_name}...", end=" ", flush=True)
            if self.install_package(pkg_name, pkg_path):
                print()
            else:
                print()
        
        return True
    
    def report(self):
        """输出报告"""
        print(f"\n{BLUE}{'='*70}{NC}")
        print(f"{BLUE}安装报告{NC}")
        print(f"{BLUE}{'='*70}{NC}\n")
        
        if self.installed:
            print(f"{GREEN}✓ 成功安装 {len(self.installed)} 个包:{NC}")
            for pkg in self.installed[:5]:
                print(f"  - {pkg}")
            if len(self.installed) > 5:
                print(f"  ... 还有 {len(self.installed) - 5} 个")
            print()
        
        if self.failed:
            print(f"{RED}✗ 失败 {len(self.failed)} 个包:{NC}")
            for pkg_name, error in self.failed[:3]:
                print(f"  - {pkg_name}")
            if len(self.failed) > 3:
                print(f"  ... 还有 {len(self.failed) - 3} 个")
            print()
            return False
        else:
            print(f"{GREEN}✓ 全部安装成功！{NC}\n")
            return True


def show_usage():
    """显示使用说明"""
    print(f"\n{BLUE}OpenVoiceOS 开发环境安装器{NC}\n")
    print("用法:")
    print(f"  python3 {Path(__file__).name} [工作区...]\n")
    
    print("可用的工作区:")
    for ws_name, ws_info in WORKSPACES.items():
        pkg_count = len(ws_info['packages'])
        print(f"  - {ws_name:15} {ws_info['description']:30} ({pkg_count} 包)")
    
    print(f"\n示例:")
    print(f"  python3 {Path(__file__).name}            # 安装核心工作区（默认）")
    print(f"  python3 {Path(__file__).name} core gui   # 安装核心和 GUI")
    print(f"  python3 {Path(__file__).name} audio      # 仅安装音频模块")
    print()


def main():
    """主函数"""
    engine_dir = Path(__file__).parent.absolute()
    os.chdir(engine_dir)
    
    # 解析命令行参数
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        show_usage()
        return 0
    
    # 获取要安装的工作区
    selected_workspaces = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_WORKSPACES
    
    # 创建管理器
    manager = WorkspaceManager(engine_dir)
    
    # 验证工作区
    valid_workspaces = manager.select_workspaces(selected_workspaces)
    
    if not valid_workspaces:
        log_error("没有选择任何有效的工作区")
        show_usage()
        return 1
    
    # 安装
    if manager.install_workspaces(valid_workspaces):
        # 输出报告
        success = manager.report()
        return 0 if success else 1
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
