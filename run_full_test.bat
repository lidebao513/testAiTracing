@echo off
setlocal enabledelayedexpansion

REM 设置项目根目录
set PROJECT_ROOT=%~dp0

REM 设置报告文件路径
set REPORT_FILE=%PROJECT_ROOT%test_report.txt

REM 设置虚拟环境路径
set VENV_PATH=%PROJECT_ROOT%venv
set ACTIVATE_SCRIPT=%VENV_PATH%\Scripts\activate.bat

REM 设置评估脚本路径
set RAGAS_SCRIPT=%PROJECT_ROOT%tests\integration\test_ragas_with_tracing.py
set DEEPEVAL_SCRIPT=%PROJECT_ROOT%tests\integration\test_deepeval_gate_on_ragapp.py

REM 清空旧报告文件
echo. > %REPORT_FILE%

REM 写入时间戳
echo ======================================================== >> %REPORT_FILE%
echo 测试执行时间: %date% %time% >> %REPORT_FILE%
echo ======================================================== >> %REPORT_FILE%
echo. >> %REPORT_FILE%

REM 1. RAGApp API 健康检查
echo [步骤 1] RAGApp API 健康检查 >> %REPORT_FILE%
echo -------------------------------------------------------- >> %REPORT_FILE%

echo 正在检查 RAGApp 服务状态...
echo 正在检查 RAGApp 服务状态... >> %REPORT_FILE%

REM 使用 curl 检查健康状态
curl -s -o health_response.txt -w "%%{http_code}" http://localhost:8000/health > http_status.txt

set /p HTTP_STATUS=<http_status.txt
set /p HEALTH_RESPONSE=<health_response.txt

del http_status.txt
del health_response.txt

if "%HTTP_STATUS%" equ "200" (
    echo RAGApp 服务状态: 正常 [HTTP %HTTP_STATUS%] >> %REPORT_FILE%
    echo RAGApp 服务状态: 正常 [HTTP %HTTP_STATUS%]
    echo 响应内容: %HEALTH_RESPONSE% >> %REPORT_FILE%
) else (
    echo RAGApp 服务状态: 异常 [HTTP %HTTP_STATUS%] >> %REPORT_FILE%
    echo RAGApp 服务状态: 异常 [HTTP %HTTP_STATUS%]
    echo 错误: 请手动启动 RAGApp 服务 >> %REPORT_FILE%
    echo 错误: 请手动启动 RAGApp 服务
    echo 启动命令示例: python -m uvicorn app:app --host 0.0.0.0 --port 8000 >> %REPORT_FILE%
    echo 启动命令示例: python -m uvicorn app:app --host 0.0.0.0 --port 8000
    echo. >> %REPORT_FILE%
    echo 测试流程终止 >> %REPORT_FILE%
    echo 测试流程终止
    goto :open_report
)

echo. >> %REPORT_FILE%

REM 2. 虚拟环境激活流程
echo [步骤 2] 虚拟环境激活 >> %REPORT_FILE%
echo -------------------------------------------------------- >> %REPORT_FILE%

echo 正在激活虚拟环境...
echo 正在激活虚拟环境... >> %REPORT_FILE%

if exist "%ACTIVATE_SCRIPT%" (
    call "%ACTIVATE_SCRIPT%"
    if %errorlevel% equ 0 (
        echo 虚拟环境激活成功 >> %REPORT_FILE%
        echo 虚拟环境激活成功
    ) else (
        echo 虚拟环境激活失败 >> %REPORT_FILE%
        echo 虚拟环境激活失败
        echo 错误: 无法激活虚拟环境，请检查 %ACTIVATE_SCRIPT% 是否存在 >> %REPORT_FILE%
        echo 错误: 无法激活虚拟环境，请检查 %ACTIVATE_SCRIPT% 是否存在
        echo. >> %REPORT_FILE%
        echo 测试流程终止 >> %REPORT_FILE%
        echo 测试流程终止
        goto :open_report
    )
) else (
    echo 虚拟环境激活失败 >> %REPORT_FILE%
    echo 虚拟环境激活失败
    echo 错误: 虚拟环境激活脚本不存在: %ACTIVATE_SCRIPT% >> %REPORT_FILE%
    echo 错误: 虚拟环境激活脚本不存在: %ACTIVATE_SCRIPT%
    echo. >> %REPORT_FILE%
    echo 测试流程终止 >> %REPORT_FILE%
    echo 测试流程终止
    goto :open_report
)

echo. >> %REPORT_FILE%

REM 3. RAGAS 评估执行
echo [步骤 3] RAGAS 评估执行 >> %REPORT_FILE%
echo -------------------------------------------------------- >> %REPORT_FILE%

echo 正在执行 RAGAS 评估...
echo 正在执行 RAGAS 评估... >> %REPORT_FILE%

if exist "%RAGAS_SCRIPT%" (
    python "%RAGAS_SCRIPT%" >> %REPORT_FILE%
    if %errorlevel% equ 0 (
        echo RAGAS 评估执行成功 >> %REPORT_FILE%
        echo RAGAS 评估执行成功
    ) else (
        echo RAGAS 评估执行失败 >> %REPORT_FILE%
        echo RAGAS 评估执行失败
        echo 错误: RAGAS 评估脚本执行出错 >> %REPORT_FILE%
        echo 错误: RAGAS 评估脚本执行出错
        echo. >> %REPORT_FILE%
        echo 测试流程终止 >> %REPORT_FILE%
        echo 测试流程终止
        goto :open_report
    )
) else (
    echo RAGAS 评估执行失败 >> %REPORT_FILE%
    echo RAGAS 评估执行失败
    echo 错误: RAGAS 评估脚本不存在: %RAGAS_SCRIPT% >> %REPORT_FILE%
    echo 错误: RAGAS 评估脚本不存在: %RAGAS_SCRIPT%
    echo. >> %REPORT_FILE%
    echo 测试流程终止 >> %REPORT_FILE%
    echo 测试流程终止
    goto :open_report
)

echo. >> %REPORT_FILE%

REM 4. DeepEval 门禁检查
echo [步骤 4] DeepEval 门禁检查 >> %REPORT_FILE%
echo -------------------------------------------------------- >> %REPORT_FILE%

echo 正在执行 DeepEval 门禁检查...
echo 正在执行 DeepEval 门禁检查... >> %REPORT_FILE%

if exist "%DEEPEVAL_SCRIPT%" (
    python "%DEEPEVAL_SCRIPT%" >> %REPORT_FILE%
    if %errorlevel% equ 0 (
        echo DeepEval 门禁检查执行成功 >> %REPORT_FILE%
        echo DeepEval 门禁检查执行成功
    ) else (
        echo DeepEval 门禁检查执行失败 >> %REPORT_FILE%
        echo DeepEval 门禁检查执行失败
        echo 错误: DeepEval 门禁脚本执行出错 >> %REPORT_FILE%
        echo 错误: DeepEval 门禁脚本执行出错
    )
) else (
    echo DeepEval 门禁检查执行失败 >> %REPORT_FILE%
    echo DeepEval 门禁检查执行失败
    echo 错误: DeepEval 门禁脚本不存在: %DEEPEVAL_SCRIPT% >> %REPORT_FILE%
    echo 错误: DeepEval 门禁脚本不存在: %DEEPEVAL_SCRIPT%
)

echo. >> %REPORT_FILE%

REM 5. 测试报告摘要
echo [步骤 5] 测试报告摘要 >> %REPORT_FILE%
echo -------------------------------------------------------- >> %REPORT_FILE%
echo 测试流程已完成 >> %REPORT_FILE%
echo 详细结果请查看上述输出 >> %REPORT_FILE%
echo. >> %REPORT_FILE%
echo ======================================================== >> %REPORT_FILE%
echo 测试执行完成: %date% %time% >> %REPORT_FILE%
echo ======================================================== >> %REPORT_FILE%

:open_report
REM 打开测试报告
echo 正在打开测试报告...
start "" "%REPORT_FILE%"

endlocal
