#!/usr/bin/env python3
"""
version-manager - 版本管理核心模块
用途：提供备份、标记、对比、强制执行等功能
"""

import os
import sys
import shutil
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"

class VersionManager:
    """版本管理器"""
    
    def __init__(self, skill_name):
        self.skill_name = skill_name
        self.skill_dir = SKILLS_DIR / skill_name
        self.versions_dir = self.skill_dir / "versions"
        self.releases_dir = WORKSPACE_DIR / "releases"
        self.version_file = self.skill_dir / "VERSION"
        self.changelog_file = self.skill_dir / "CHANGELOG.md"
        self.backup_config_file = self.skill_dir / "backup_config.json"
        
        # 本地备份保留数量 (配置为 1 个)
        self.local_keep_count = 1
    
    def get_current_version(self):
        """获取当前版本号"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "v0.0.0"
    
    def backup(self, training_goal="", include_related=True):
        """
        训练前备份
        
        Args:
            training_goal: 训练目标
            include_related: 是否包含相关文件 (脚本、模板等)
        
        Returns:
            backup_name: 备份名称
        """
        current_version = self.get_current_version()
        date = datetime.now().strftime("%Y%m%d")
        backup_name = f"{current_version}-{date}-pre-training"
        backup_path = self.versions_dir / backup_name
        
        print(f"📦 开始备份技能：{self.skill_name} (当前版本：{current_version})")
        
        # 创建版本目录
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份技能目录
        print(f"   备份技能文件...")
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(self.skill_dir, backup_path)
        
        # 清理备份中的 versions 目录 (避免递归)
        backup_versions = backup_path / "versions"
        if backup_versions.exists():
            shutil.rmtree(backup_versions)
        
        # 记录训练目标
        if training_goal:
            (backup_path / "training_goal.txt").write_text(training_goal)
            print(f"   记录训练目标：{training_goal}")
        
        # 备份相关文件
        if include_related:
            print(f"   备份相关文件...")
            related_files_dir = backup_path / "related_files"
            related_files_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份脚本文件
            scripts_dir = WORKSPACE_DIR / "scripts"
            if scripts_dir.exists():
                for file in scripts_dir.glob(f"*{self.skill_name}*"):
                    dest_dir = related_files_dir / "scripts"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest_dir)
                    print(f"     - scripts/{file.name}")
            
            # 备份模板文件
            templates_dir = WORKSPACE_DIR / "templates"
            if templates_dir.exists():
                for file in templates_dir.glob(f"*{self.skill_name}*"):
                    dest_dir = related_files_dir / "templates"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest_dir)
                    print(f"     - templates/{file.name}")
            
            # 备份最近输出文件 (7 天内)
            output_dir = WORKSPACE_DIR / "output"
            if output_dir.exists():
                dest_dir = related_files_dir / "output"
                dest_dir.mkdir(parents=True, exist_ok=True)
                import time
                for file in output_dir.glob(f"*{self.skill_name}*"):
                    if time.time() - file.stat().st_mtime < 7 * 24 * 60 * 60:
                        shutil.copy2(file, dest_dir)
                        print(f"     - output/{file.name}")
        
        # 生成备份清单
        manifest_content = f"""备份清单
========
技能名称：{self.skill_name}
备份版本：{backup_name}
备份时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
训练目标：{training_goal or '未指定'}

备份文件列表:
"""
        for file in sorted(backup_path.rglob("*")):
            if file.is_file():
                rel_path = file.relative_to(backup_path)
                manifest_content += f"  - {rel_path}\n"
        
        (backup_path / "BACKUP_MANIFEST.txt").write_text(manifest_content)
        
        # 计算备份大小
        backup_size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file())
        backup_size_mb = backup_size / 1024 / 1024
        
        print(f"✅ 备份完成：{backup_name}")
        print(f"   备份位置：{backup_path}")
        print(f"   备份大小：{backup_size_mb:.1f} MB")
        
        return backup_name
    
    def tag(self, version, changes=None):
        """
        标记新版本
        
        Args:
            version: 新版本号
            changes: 变更内容字典 {fixed: [], improved: [], changed: []}
        """
        print(f"🏷️  标记技能版本：{self.skill_name} -> {version}")
        
        # 更新版本号
        self.version_file.write_text(version)
        print(f"   ✅ 已更新 VERSION 文件")
        
        # 更新 CHANGELOG
        if not self.changelog_file.exists():
            self.changelog_file.write_text(f"# {self.skill_name} 变更日志\n\n")
        
        # 添加新版本条目
        changelog_entry = f"""
## {version} - {datetime.now().strftime('%Y-%m-%d')}

"""
        if changes:
            if changes.get('fixed'):
                changelog_entry += "### 修复\n"
                for item in changes['fixed']:
                    changelog_entry += f"- {item}\n"
                changelog_entry += "\n"
            
            if changes.get('improved'):
                changelog_entry += "### 改进\n"
                for item in changes['improved']:
                    changelog_entry += f"- {item}\n"
                changelog_entry += "\n"
            
            if changes.get('changed'):
                changelog_entry += "### 变更\n"
                for item in changes['changed']:
                    changelog_entry += f"- {item}\n"
                changelog_entry += "\n"
        
        with open(self.changelog_file, 'a') as f:
            f.write(changelog_entry)
        
        print(f"   ✅ 已更新 CHANGELOG.md")
        
        # 更新相关文件版本号
        print(f"   更新相关文件版本...")
        self._update_related_files_version(version)
        
        print(f"✅ 版本标记完成：{version}")
    
    def _update_related_files_version(self, version):
        """更新相关文件版本号"""
        # 更新脚本文件
        scripts_dir = WORKSPACE_DIR / "scripts"
        if scripts_dir.exists():
            for file in scripts_dir.glob(f"*{self.skill_name}*.py"):
                # 移除旧版本号，添加新版本号
                import re
                new_name = re.sub(r'-v\d+\.\d+\.\d+', '', file.stem) + f"-{version}.py"
                new_path = scripts_dir / new_name
                if str(file) != str(new_path):
                    shutil.copy2(file, new_path)
                    print(f"     - scripts/{new_name}")
        
        # 更新模板文件
        templates_dir = WORKSPACE_DIR / "templates"
        if templates_dir.exists():
            for file in templates_dir.glob(f"*{self.skill_name}*.xlsx"):
                import re
                new_name = re.sub(r'-v\d+\.\d+\.\d+', '', file.stem) + f"-{version}.xlsx"
                new_path = templates_dir / new_name
                if str(file) != str(new_path):
                    shutil.copy2(file, new_path)
                    print(f"     - templates/{new_name}")
    
    def compare(self, old_version, new_version=None):
        """
        对比两个版本
        
        Args:
            old_version: 旧版本号
            new_version: 新版本号 (None 表示与当前版本对比)
        
        Returns:
            diff_info: 差异信息字典
        """
        if new_version is None:
            new_version = self.get_current_version()
            path2 = self.skill_dir
        else:
            path2 = self.versions_dir / new_version
        
        path1 = self.versions_dir / old_version
        
        if not path1.exists():
            raise FileNotFoundError(f"版本不存在：{old_version}")
        
        if not path2.exists():
            raise FileNotFoundError(f"版本不存在：{new_version}")
        
        print(f"🔍 对比版本：{old_version} vs {new_version}")
        
        # 生成差异报告
        import subprocess
        diff_file = Path("/tmp") / f"{self.skill_name}-{old_version}-vs-{new_version}.diff"
        
        result = subprocess.run(
            ["diff", "-rq", str(path1), str(path2)],
            capture_output=True,
            text=True
        )
        
        diff_file.write_text(result.stdout)
        
        # 解析差异
        diff_info = {
            'added': [],
            'removed': [],
            'modified': [],
            'summary': result.stdout
        }
        
        for line in result.stdout.split('\n'):
            if line.startswith('Only in'):
                if 'new_version' in line or path2.name in line:
                    diff_info['added'].append(line)
                else:
                    diff_info['removed'].append(line)
            elif line.startswith('Files'):
                diff_info['modified'].append(line)
        
        if diff_info['summary']:
            print(f"   差异文件列表:")
            for line in diff_info['summary'].split('\n')[:10]:
                if line:
                    print(f"     {line}")
            print(f"\n   完整差异报告：{diff_file}")
        else:
            print(f"   ⚠️  两个版本无差异")
        
        return diff_info
    
    def list_versions(self):
        """列出所有版本"""
        if not self.versions_dir.exists():
            return []
        
        versions = []
        for v in sorted(self.versions_dir.iterdir(), reverse=True):
            if v.is_dir():
                versions.append(v.name)
        
        current = self.get_current_version()
        
        print(f"📋 技能版本列表：{self.skill_name}")
        print(f"\n当前版本：{current}")
        print(f"\n历史版本:")
        print("-" * 40)
        
        for version in versions:
            # 提取日期
            import re
            date_match = re.search(r'(\d{8})', version)
            if date_match:
                date_str = date_match.group(1)
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                print(f"  - {version} ({formatted_date})")
            else:
                print(f"  - {version}")
        
        return versions
    
    def clean(self, keep=None):
        """
        清理旧版本
        
        Args:
            keep: 保留的版本数量 (默认使用 self.local_keep_count = 1)
        """
        if keep is None:
            keep = self.local_keep_count
            
        if not self.versions_dir.exists():
            print("⚠️  无历史版本可清理")
            return
        
        versions = sorted(self.versions_dir.iterdir())
        count = len(versions)
        to_delete = count - keep
        
        if to_delete <= 0:
            print(f"✅ 无需清理 (当前 {count} 个版本)")
            return
        
        print(f"🧹 清理旧版本 (保留最近 {keep} 个)...")
        
        for version in versions[:to_delete]:
            print(f"   删除旧版本：{version.name}")
            shutil.rmtree(version)
        
        print(f"✅ 已清理 {to_delete} 个旧版本")
    
    def status(self):
        """显示技能状态"""
        current_version = self.get_current_version()
        
        print(f"📊 技能状态：{self.skill_name}")
        print(f"\n当前版本：{current_version}")
        print(f"技能目录：{self.skill_dir}")
        print(f"版本目录：{self.versions_dir}")
        
        # 统计版本数量
        if self.versions_dir.exists():
            version_count = len(list(self.versions_dir.iterdir()))
            print(f"\n历史版本数：{version_count}")
        else:
            print(f"\n历史版本数：0")
        
        # 检查相关文件
        print(f"\n相关文件:")
        
        scripts_dir = WORKSPACE_DIR / "scripts"
        if scripts_dir.exists():
            script_count = len(list(scripts_dir.glob(f"*{self.skill_name}*")))
            print(f"  - 脚本文件：{script_count}")
        
        templates_dir = WORKSPACE_DIR / "templates"
        if templates_dir.exists():
            template_count = len(list(templates_dir.glob(f"*{self.skill_name}*")))
            print(f"  - 模板文件：{template_count}")
        
        output_dir = WORKSPACE_DIR / "output"
        if output_dir.exists():
            import time
            output_count = sum(1 for f in output_dir.glob(f"*{self.skill_name}*") 
                             if time.time() - f.stat().st_mtime < 7 * 24 * 60 * 60)
            print(f"  - 最近输出：{output_count} (7 天内)")


# 便捷函数
def backup(skill_name, training_goal="", include_related=True):
    """训练前备份"""
    manager = VersionManager(skill_name)
    return manager.backup(training_goal, include_related)

def tag(skill_name, version, changes=None):
    """标记新版本"""
    manager = VersionManager(skill_name)
    return manager.tag(version, changes)

def compare(skill_name, old_version, new_version=None):
    """版本对比"""
    manager = VersionManager(skill_name)
    return manager.compare(old_version, new_version)

def list_versions(skill_name):
    """列出所有版本"""
    manager = VersionManager(skill_name)
    return manager.list_versions()

def clean(skill_name, keep=3):
    """清理旧版本"""
    manager = VersionManager(skill_name)
    return manager.clean(keep)

def status(skill_name):
    """显示状态"""
    manager = VersionManager(skill_name)
    return manager.status()

def pre_training_check(skill_name, training_goal):
    """训练前强制检查"""
    print(f"🔍 训练前检查：{skill_name}")
    manager = VersionManager(skill_name)
    
    # 检查是否已备份
    if manager.versions_dir.exists():
        latest_backup = max(manager.versions_dir.iterdir(), key=lambda x: x.stat().st_mtime, default=None)
        if latest_backup:
            import time
            backup_age = time.time() - latest_backup.stat().st_mtime
            if backup_age < 3600:  # 1 小时内有备份
                print(f"   ✅ 已有备份 (备份时间：{datetime.fromtimestamp(latest_backup.stat().st_mtime)})")
                return True
    
    # 需要备份
    print(f"   ⚠️  未找到备份，创建备份...")
    manager.backup(training_goal)
    print(f"   ✅ 备份完成")
    return True

def post_training_verify(skill_name, new_version):
    """训练后强制验证"""
    print(f"🔍 训练后验证：{skill_name}")
    
    # 检查版本号是否更新
    manager = VersionManager(skill_name)
    current_version = manager.get_current_version()
    
    if current_version == new_version:
        print(f"   ✅ 版本号已更新：{new_version}")
    else:
        print(f"   ❌ 版本号未更新 (期望：{new_version}, 当前：{current_version})")
        return False
    
    # 检查 CHANGELOG
    if manager.changelog_file.exists():
        content = manager.changelog_file.read_text()
        if new_version in content:
            print(f"   ✅ CHANGELOG.md 已更新")
        else:
            print(f"   ❌ CHANGELOG.md 未包含新版本")
            return False
    else:
        print(f"   ❌ CHANGELOG.md 不存在")
        return False
    
    print(f"   ✅ 验证通过")
    return True


def publish_github(skill_name, version=None, create_release=True):
    """
    发布技能到 GitHub
    
    Args:
        skill_name: 技能名称
        version: 版本号 (None 表示使用当前版本)
        create_release: 是否创建 GitHub Release
    """
    manager = VersionManager(skill_name)
    
    if version is None:
        version = manager.get_current_version()
    
    print(f"🚀 发布技能到 GitHub: {skill_name} ({version})")
    
    # 1. 生成技能包
    print(f"   生成技能包...")
    package_path = manager.releases_dir / f"{skill_name}-{version}.tar.gz"
    manager.releases_dir.mkdir(parents=True, exist_ok=True)
    
    # 打包技能文件
    import tarfile
    with tarfile.open(package_path, "w:gz") as tar:
        tar.add(manager.skill_dir, arcname=skill_name)
    
    # 生成校验和
    import hashlib
    sha256_hash = hashlib.sha256(package_path.read_bytes()).hexdigest()
    sha256_path = package_path.with_suffix(".tar.gz.sha256")
    sha256_path.write_text(f"{sha256_hash}  {package_path.name}")
    
    print(f"   ✅ 技能包：{package_path}")
    print(f"   ✅ 校验和：{sha256_path}")
    
    # 2. 创建 GitHub Release
    if create_release:
        print(f"   创建 GitHub Release...")
        
        # 使用 gh CLI
        try:
            import subprocess
            
            # 获取 release notes
            changelog = ""
            if manager.changelog_file.exists():
                content = manager.changelog_file.read_text()
                # 提取当前版本的变更日志
                import re
                match = re.search(rf'## {version}.*?(?=## |$)', content, re.DOTALL)
                if match:
                    changelog = match.group(0).strip()
            
            # 创建 release
            cmd = [
                "gh", "release", "create", version,
                str(package_path), str(sha256_path),
                "--title", f"{skill_name} {version}",
                "--notes", changelog if changelog else f"Release {version}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE_DIR))
            
            if result.returncode == 0:
                print(f"   ✅ GitHub Release 创建成功")
                release_url = f"https://github.com/RenLimin/openclaw-backup/releases/tag/{version}"
                print(f"   🔗 {release_url}")
            else:
                print(f"   ⚠️  GitHub CLI 执行失败：{result.stderr}")
                print(f"   请手动创建 Release")
                
        except FileNotFoundError:
            print(f"   ⚠️  gh CLI 未安装，请手动创建 Release")
            print(f"   命令：gh release create {version} {package_path} --title '{skill_name} {version}'")
        except Exception as e:
            print(f"   ⚠️  创建 Release 失败：{e}")
    
    # 3. 更新发布索引
    print(f"   更新发布索引...")
    index_file = manager.releases_dir / "release_index.json"
    
    if index_file.exists():
        index = json.loads(index_file.read_text())
    else:
        index = {"skills": {}}
    
    if skill_name not in index["skills"]:
        index["skills"][skill_name] = []
    
    # 添加新 release
    release_info = {
        "version": version,
        "package": str(package_path),
        "sha256": str(sha256_path),
        "releasedAt": datetime.now().isoformat(),
        "github": f"https://github.com/RenLimin/openclaw-backup/releases/tag/{version}" if create_release else None
    }
    index["skills"][skill_name].append(release_info)
    
    # 保留最近 10 个 release
    index["skills"][skill_name] = index["skills"][skill_name][-10:]
    
    index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    print(f"   ✅ 发布索引已更新")
    
    print(f"✅ 发布完成：{skill_name} ({version})")
    return package_path


# 命令行入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 -m skills.version_manager <command> [args]")
        print("命令：backup, tag, compare, list, clean, status, publish-github")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        goal = sys.argv[3] if len(sys.argv) > 3 else ""
        if not skill:
            print("❌ 请指定技能名称")
            sys.exit(1)
        backup(skill, goal)
    
    elif command == "tag":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        version = sys.argv[3] if len(sys.argv) > 3 else None
        if not skill or not version:
            print("❌ 请指定技能名称和版本号")
            sys.exit(1)
        tag(skill, version)
    
    elif command == "compare":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        old = sys.argv[3] if len(sys.argv) > 3 else None
        new = sys.argv[4] if len(sys.argv) > 4 else None
        if not skill or not old:
            print("❌ 请指定技能名称和旧版本号")
            sys.exit(1)
        compare(skill, old, new)
    
    elif command == "list":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        if not skill:
            print("❌ 请指定技能名称")
            sys.exit(1)
        list_versions(skill)
    
    elif command == "clean":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        keep = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        if not skill:
            print("❌ 请指定技能名称")
            sys.exit(1)
        clean(skill, keep)
    
    elif command == "status":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        if not skill:
            print("❌ 请指定技能名称")
            sys.exit(1)
        status(skill)
    
    elif command == "publish-github":
        skill = sys.argv[2] if len(sys.argv) > 2 else None
        version = sys.argv[3] if len(sys.argv) > 3 else None
        if not skill:
            print("❌ 请指定技能名称")
            sys.exit(1)
        publish_github(skill, version)
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)
