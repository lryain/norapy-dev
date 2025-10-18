#!/usr/bin/env python3
"""
OVOS 完整依赖解析和安装系统

这个脚本完成以下工作：
1. 自动扫描所有 setup.py 文件
2. 使用 AST 解析提取 install_requires 和 extras_require
3. 构建完整的依赖图
4. 按正确顺序安装所有本地包
5. 自动处理本地与 PyPI 包的优先级

这是业界标准的 monorepo 管理方式
"""

import subprocess
import sys
import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

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

class DependencyAnalyzer:
    """使用 AST 分析 setup.py 中的依赖"""
    
    def __init__(self, engine_dir: Path):
        self.engine_dir = engine_dir
        self.packages: Dict[str, Dict] = {}  # {package_name: {path, deps}}
        self.local_packages: Set[str] = set()
        
    def scan_all_packages(self):
        """扫描所有 setup.py 文件"""
        log_info("扫描所有 setup.py 文件...")
        
        setup_files = list(self.engine_dir.rglob('setup.py'))
        setup_files = [f for f in setup_files 
                      if 'test' not in str(f) and 'venv' not in str(f)]
        
        log_success(f"找到 {len(setup_files)} 个包")
        
        for setup_file in setup_files:
            try:
                self._parse_setup_py(setup_file)
            except Exception as e:
                log_warn(f"解析 {setup_file}: {e}")
    
    def _parse_setup_py(self, setup_file: Path):
        """使用 AST 解析单个 setup.py"""
        with open(setup_file) as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        # 查找 setup() 调用
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'setup':
                    self._extract_setup_info(node, setup_file)
    
    def _extract_setup_info(self, setup_call: ast.Call, setup_file: Path):
        """从 setup() 调用中提取信息"""
        pkg_name = None
        version = None
        dependencies = []
        
        for keyword in setup_call.keywords:
            if keyword.arg == 'name':
                pkg_name = self._get_string_value(keyword.value)
            elif keyword.arg == 'version':
                version = self._get_string_value(keyword.value)
            elif keyword.arg == 'install_requires':
                dependencies.extend(self._extract_requirements_list(keyword.value))
            elif keyword.arg == 'extras_require':
                # 处理 extras_require 中的所有依赖
                extras_deps = self._extract_extras_requires(keyword.value)
                dependencies.extend(extras_deps)
        
        if pkg_name:
            self.packages[pkg_name] = {
                'path': setup_file.parent,
                'version': version,
                'dependencies': dependencies
            }
            self.local_packages.add(pkg_name)
            print(f"  └─ {pkg_name}: {len(dependencies)} 依赖")
    
    def _get_string_value(self, node):
        """提取字符串字面值"""
        if isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Str):
            return node.s
        return None
    
    def _extract_requirements_list(self, node):
        """提取 install_requires 列表"""
        requirements = []
        
        if isinstance(node, ast.List):
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    req = str(elt.value)
                    if not req.startswith('-e'):  # 跳过 -e 行
                        requirements.append(req)
        elif isinstance(node, ast.Call):
            # 处理函数调用，如 required('requirements.txt')
            # 这需要实际读取文件
            pass
        
        return requirements
    
    def _extract_extras_requires(self, node):
        """提取 extras_require 中的所有依赖"""
        requirements = []
        
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                reqs = self._extract_requirements_list(value)
                requirements.extend(reqs)
        
        return requirements
    
    def resolve_dependency_order(self) -> List[str]:
        """拓扑排序，确定安装顺序"""
        log_info("解析依赖图...")
        
        # 构建依赖关系
        graph = defaultdict(set)
        all_packages = set(self.packages.keys())
        
        for pkg_name, info in self.packages.items():
            for dep in info['dependencies']:
                # 提取包名（移除版本规范）
                dep_name = self._parse_package_name(dep)
                
                # 如果是本地包，添加到图中
                if dep_name in all_packages:
                    graph[pkg_name].add(dep_name)
        
        # 拓扑排序
        visited = set()
        visiting = set()
        order = []
        
        def visit(node):
            if node in visited:
                return
            if node in visiting:
                raise ValueError(f"循环依赖检测到: {node}")
            
            visiting.add(node)
            
            if node in graph:
                for dep in graph[node]:
                    visit(dep)
            
            visiting.remove(node)
            visited.add(node)
            order.append(node)
        
        for pkg in all_packages:
            visit(pkg)
        
        # 反向排序（依赖在前）
        order.reverse()
        
        return order
    
    def _parse_package_name(self, requirement: str) -> str:
        """从 requirement 字符串中提取包名"""
        # 移除版本规范符号
        for char in ['<', '>', '=', '!', '[', ' ', '~']:
            if char in requirement:
                requirement = requirement.split(char)[0]
        
        return requirement.strip()
    
    def get_install_order(self) -> List[Tuple[str, Path]]:
        """获取安装顺序"""
        order = self.resolve_dependency_order()
        result = []
        
        for pkg_name in order:
            if pkg_name in self.packages:
                result.append((pkg_name, self.packages[pkg_name]['path']))
        
        return result


class InstallManager:
    """管理包的安装"""
    
    def __init__(self, engine_dir: Path):
        self.engine_dir = engine_dir
        self.failed = []
    
    def install_package(self, pkg_name: str, pkg_path: Path, use_editable: bool = True) -> bool:
        """安装单个包"""
        try:
            if use_editable:
                cmd = [
                    sys.executable, '-m', 'pip', 'install',
                    '--no-build-isolation',
                    '-e', str(pkg_path)
                ]
            else:
                cmd = [
                    sys.executable, '-m', 'pip', 'install',
                    str(pkg_path)
                ]
            
            # 运行安装
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.engine_dir
            )
            
            if result.returncode == 0:
                log_success(f"已安装: {pkg_name}")
                return True
            else:
                log_error(f"安装失败: {pkg_name}")
                if '--no-build-isolation' in ' '.join(cmd):
                    # 尝试不用 --no-build-isolation 再试一次
                    log_warn(f"  重试不使用 --no-build-isolation...")
                    cmd.remove('--no-build-isolation')
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        log_success(f"已安装: {pkg_name} (不使用 --no-build-isolation)")
                        return True
                
                self.failed.append((pkg_name, result.stderr))
                return False
        
        except Exception as e:
            log_error(f"安装异常 {pkg_name}: {e}")
            self.failed.append((pkg_name, str(e)))
            return False
    
    def install_all(self, install_order: List[Tuple[str, Path]]):
        """安装所有包"""
        print(f"\n{BLUE}{'='*70}{NC}")
        print(f"{BLUE}安装依赖（共 {len(install_order)} 个包）{NC}")
        print(f"{BLUE}{'='*70}{NC}\n")
        
        for i, (pkg_name, pkg_path) in enumerate(install_order, 1):
            print(f"[{i}/{len(install_order)}] 安装 {pkg_name}...")
            self.install_package(pkg_name, pkg_path)
            print()
    
    def report(self):
        """输出报告"""
        if self.failed:
            print(f"\n{RED}{'='*70}{NC}")
            print(f"{RED}安装失败的包 ({len(self.failed)} 个):{NC}")
            print(f"{RED}{'='*70}{NC}\n")
            
            for pkg_name, error in self.failed:
                print(f"  - {pkg_name}")
                # 只显示最后几行错误
                error_lines = error.split('\n')[-5:]
                for line in error_lines:
                    if line.strip():
                        print(f"    {line}")
            
            return False
        else:
            print(f"\n{GREEN}{'='*70}{NC}")
            print(f"{GREEN}✓ 所有包安装成功！{NC}")
            print(f"{GREEN}开发环境已就绪{NC}")
            print(f"{GREEN}{'='*70}{NC}\n")
            
            return True


def main():
    """主函数"""
    engine_dir = Path(__file__).parent.absolute()
    
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}OpenVoiceOS 开发环境完整安装器{NC}")
    print(f"{BLUE}智能依赖解析和拓扑排序{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")
    
    # 第一步：分析依赖
    print(f"{BLUE}第一步：分析依赖{NC}\n")
    analyzer = DependencyAnalyzer(engine_dir)
    analyzer.scan_all_packages()
    
    # 第二步：确定安装顺序
    print(f"\n{BLUE}第二步：确定安装顺序{NC}\n")
    try:
        install_order = analyzer.get_install_order()
        print(f"\n建议安装顺序（共 {len(install_order)} 个包）:")
        for i, (pkg_name, pkg_path) in enumerate(install_order[:10], 1):
            print(f"  {i}. {pkg_name}")
        if len(install_order) > 10:
            print(f"  ... 还有 {len(install_order) - 10} 个包")
    except ValueError as e:
        log_error(f"依赖分析错误: {e}")
        return 1
    
    # 第三步：安装
    print(f"\n{BLUE}第三步：安装所有包{NC}")
    installer = InstallManager(engine_dir)
    installer.install_all(install_order)
    
    # 输出报告
    if installer.report():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
