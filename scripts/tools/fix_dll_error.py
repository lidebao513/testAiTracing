#!/usr/bin/env python3
"""
DLL 加载错误修复脚本

功能：
1. 检测当前操作系统是否为 Windows
2. 打印当前的 Python 解释器路径和虚拟环境路径
3. 提供修复步骤的自动执行或打印手动执行命令
4. 提供详细的排查指引
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_windows():
    """检测当前操作系统是否为 Windows"""
    current_os = platform.system()
    is_windows = current_os == "Windows"
    
    logger.info(f"当前操作系统: {current_os}")
    logger.info(f"是否为 Windows: {is_windows}")
    
    return is_windows


def print_python_info():
    """打印当前的 Python 解释器路径和虚拟环境路径"""
    logger.info("\n=== Python 环境信息 ===")
    
    # Python 解释器路径
    python_executable = sys.executable
    logger.info(f"Python 解释器路径: {python_executable}")
    
    # Python 版本
    python_version = platform.python_version()
    logger.info(f"Python 版本: {python_version}")
    
    # 虚拟环境路径
    virtual_env = os.environ.get('VIRTUAL_ENV', '未检测到虚拟环境')
    logger.info(f"虚拟环境路径: {virtual_env}")
    
    # Python 路径
    logger.info(f"Python 路径: {sys.path}")
    
    return python_executable, virtual_env


def run_command(command, description):
    """运行命令并返回结果"""
    logger.info(f"\n执行: {description}")
    logger.info(f"命令: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info(f"✓ {description} 成功")
            if result.stdout:
                logger.info(f"输出: {result.stdout[:500]}")  # 限制输出长度
            return True
        else:
            logger.error(f"✗ {description} 失败")
            logger.error(f"错误: {result.stderr[:500]}")
            return False
    except Exception as e:
        logger.error(f"✗ {description} 异常: {str(e)}")
        return False


def fix_cryptography():
    """修复 cryptography 相关的 DLL 加载问题"""
    logger.info("\n=== 开始修复 cryptography 相关问题 ===")
    
    # 1. 卸载 cryptography、pyOpenSSL、certifi
    packages = ["cryptography", "pyOpenSSL", "certifi"]
    
    for package in packages:
        run_command(f"pip uninstall -y {package}", f"卸载 {package}")
    
    # 2. 清理 pip 缓存
    run_command("pip cache purge", "清理 pip 缓存")
    
    # 3. 重新安装 certifi
    run_command("pip install certifi", "重新安装 certifi")
    
    # 4. 尝试从源码重新编译 cryptography
    logger.info("\n尝试从源码重新编译 cryptography...")
    logger.info("注意：这需要系统安装有编译环境（Visual C++ Build Tools）")
    
    # 检查是否有编译环境
    has_compiler = check_compiler()
    
    if has_compiler:
        logger.info("检测到编译环境，尝试从源码编译...")
        success = run_command(
            "pip install cryptography --no-binary cryptography",
            "从源码编译安装 cryptography"
        )
        
        if not success:
            logger.warning("从源码编译失败，尝试安装预编译版本...")
            run_command("pip install cryptography", "安装预编译版本 cryptography")
    else:
        logger.warning("未检测到编译环境，安装预编译版本...")
        run_command("pip install cryptography", "安装预编译版本 cryptography")
    
    # 5. 安装 pyOpenSSL
    run_command("pip install pyOpenSSL", "重新安装 pyOpenSSL")
    
    logger.info("\n=== 修复完成 ===")


def check_compiler():
    """检查系统是否有编译环境"""
    logger.info("检查编译环境...")
    
    # 检查 cl.exe（Visual C++ 编译器）
    try:
        result = subprocess.run(
            ["cl"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "Microsoft" in result.stdout or "Microsoft" in result.stderr:
            logger.info("✓ 检测到 Visual C++ 编译器")
            return True
    except:
        pass
    
    # 检查 gcc
    try:
        result = subprocess.run(
            ["gcc", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("✓ 检测到 GCC 编译器")
            return True
    except:
        pass
    
    logger.info("✗ 未检测到编译环境")
    return False


def print_manual_commands():
    """打印需要手动执行的命令"""
    logger.info("\n=== 手动执行命令 ===")
    logger.info("如果自动修复失败，请尝试手动执行以下命令：")
    logger.info("")
    logger.info("1. 卸载问题包：")
    logger.info("   pip uninstall -y cryptography pyOpenSSL certifi")
    logger.info("")
    logger.info("2. 清理 pip 缓存：")
    logger.info("   pip cache purge")
    logger.info("")
    logger.info("3. 重新安装 certifi：")
    logger.info("   pip install certifi")
    logger.info("")
    logger.info("4. 重新安装 cryptography（预编译版本）：")
    logger.info("   pip install cryptography")
    logger.info("")
    logger.info("5. 如果需要从源码编译（需要 Visual C++ Build Tools）：")
    logger.info("   pip install cryptography --no-binary cryptography")
    logger.info("")
    logger.info("6. 重新安装 pyOpenSSL：")
    logger.info("   pip install pyOpenSSL")


def print_troubleshooting_guide():
    """打印详细的排查指引"""
    logger.info("\n=== 详细排查指引 ===")
    
    logger.info("\n1. 检查 Windows Defender 或安全软件拦截：")
    logger.info("   - 打开 Windows 安全中心")
    logger.info("   - 点击 '病毒和威胁防护'")
    logger.info("   - 查看 '保护历史记录'")
    logger.info("   - 查找是否有关于 Python 或 DLL 文件的拦截记录")
    logger.info("")
    logger.info("2. 检查公司安全软件（如 McAfee、Symantec 等）：")
    logger.info("   - 打开安全软件控制台")
    logger.info("   - 查看隔离区或威胁日志")
    logger.info("   - 查找被拦截的 Python 相关文件")
    logger.info("")
    logger.info("3. 添加目录到白名单：")
    logger.info("   需要联系管理员添加以下目录到白名单：")
    logger.info(f"   - Python 安装目录: {os.path.dirname(sys.executable)}")
    logger.info(f"   - 虚拟环境目录: {os.environ.get('VIRTUAL_ENV', 'N/A')}")
    logger.info(f"   - pip 缓存目录: {os.path.expanduser('~')}")
    logger.info("")
    logger.info("4. 临时禁用安全软件（仅用于测试）：")
    logger.info("   ⚠️ 警告：此操作存在安全风险，请在测试完成后立即重新启用")
    logger.info("   - 联系 IT 管理员获取临时禁用权限")
    logger.info("   - 在禁用期间执行修复命令")
    logger.info("   - 完成后立即重新启用安全软件")
    logger.info("")
    logger.info("5. 使用管理员权限运行：")
    logger.info("   - 右键点击命令提示符或 PowerShell")
    logger.info("   - 选择 '以管理员身份运行'")
    logger.info("   - 在管理员权限下执行修复命令")
    logger.info("")
    logger.info("6. 检查系统环境变量：")
    logger.info("   - 确保 PATH 环境变量包含 Python 和 pip 的路径")
    logger.info("   - 检查是否有冲突的 DLL 文件")


def main():
    """主函数"""
    logger.info("启动 DLL 加载错误修复脚本")
    logger.info("=" * 60)
    
    # 1. 检测操作系统
    is_windows = check_windows()
    
    if not is_windows:
        logger.warning("此脚本专为 Windows 系统设计")
        logger.info("对于其他操作系统，请手动检查 Python 环境")
        return
    
    # 2. 打印 Python 环境信息
    python_executable, virtual_env = print_python_info()
    
    # 3. 询问用户是否执行自动修复
    logger.info("\n" + "=" * 60)
    logger.info("准备执行自动修复...")
    logger.info("这将卸载并重装 cryptography、pyOpenSSL、certifi 包")
    logger.info("并清理 pip 缓存")
    
    # 自动执行修复（非交互式环境）
    logger.info("自动执行修复...")
    fix_cryptography()
    
    # 4. 打印手动命令
    print_manual_commands()
    
    # 5. 打印排查指引
    print_troubleshooting_guide()
    
    logger.info("\n" + "=" * 60)
    logger.info("脚本执行完成")
    logger.info("如果问题仍然存在，请按照上述排查指引进行操作")


if __name__ == "__main__":
    main()
