# Set project root directory
$PROJECT_ROOT = $PSScriptRoot

# Set report file path
$REPORT_FILE = Join-Path $PROJECT_ROOT "test_report.txt"

# Set evaluation script paths
$RAGAS_SCRIPT = Join-Path $PROJECT_ROOT "tests\integration\test_ragas_with_tracing.py"
$DEEPEVAL_SCRIPT = Join-Path $PROJECT_ROOT "tests\integration\test_deepeval_gate_on_ragapp.py"

# Clear old report file
"" | Out-File -FilePath $REPORT_FILE -Force

# Write timestamp
"========================================================" | Out-File -FilePath $REPORT_FILE -Append
"Test execution time: $(Get-Date)" | Out-File -FilePath $REPORT_FILE -Append
"========================================================" | Out-File -FilePath $REPORT_FILE -Append
"" | Out-File -FilePath $REPORT_FILE -Append

# 1. RAGApp API health check
"[Step 1] RAGApp API Health Check" | Out-File -FilePath $REPORT_FILE -Append
"--------------------------------------------------------" | Out-File -FilePath $REPORT_FILE -Append

Write-Host "Checking RAGApp service status..."
"Checking RAGApp service status..." | Out-File -FilePath $REPORT_FILE -Append

# Use Invoke-WebRequest to check health status
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing -ErrorAction Stop
    $HTTP_STATUS = $response.StatusCode
    $HEALTH_RESPONSE = $response.Content
    
    if ($HTTP_STATUS -eq 200) {
        "RAGApp service status: Normal [HTTP $HTTP_STATUS]" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "RAGApp service status: Normal [HTTP $HTTP_STATUS]"
        "Response content: $HEALTH_RESPONSE" | Out-File -FilePath $REPORT_FILE -Append
    } else {
        "RAGApp service status: Abnormal [HTTP $HTTP_STATUS]" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "RAGApp service status: Abnormal [HTTP $HTTP_STATUS]"
        "Error: Please start RAGApp service manually" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "Error: Please start RAGApp service manually"
        "Startup command example: python -m uvicorn app:app --host 0.0.0.0 --port 8000" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "Startup command example: python -m uvicorn app:app --host 0.0.0.0 --port 8000"
        "" | Out-File -FilePath $REPORT_FILE -Append
        "Test process terminated" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "Test process terminated"
        # Open report
        Write-Host "Opening test report..."
        Invoke-Item $REPORT_FILE
        exit 1
    }
} catch {
    "RAGApp service status: Abnormal [Cannot connect]" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "RAGApp service status: Abnormal [Cannot connect]"
    "Error: Please start RAGApp service manually" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Error: Please start RAGApp service manually"
    "Startup command example: python -m uvicorn app:app --host 0.0.0.0 --port 8000" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Startup command example: python -m uvicorn app:app --host 0.0.0.0 --port 8000"
    "" | Out-File -FilePath $REPORT_FILE -Append
    "Test process terminated" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Test process terminated"
    # Open report
    Write-Host "Opening test report..."
    Invoke-Item $REPORT_FILE
    exit 1
}

"" | Out-File -FilePath $REPORT_FILE -Append

# 2. RAGAS evaluation execution (using system Python)
"[Step 2] RAGAS Evaluation Execution" | Out-File -FilePath $REPORT_FILE -Append
"--------------------------------------------------------" | Out-File -FilePath $REPORT_FILE -Append

Write-Host "Executing RAGAS evaluation..."
"Executing RAGAS evaluation..." | Out-File -FilePath $REPORT_FILE -Append

if (Test-Path $RAGAS_SCRIPT) {
    try {
        # Use system Python instead of virtual environment
        $output = & python $RAGAS_SCRIPT 2>&1
        $output | Out-File -FilePath $REPORT_FILE -Append
        if ($LASTEXITCODE -eq 0) {
            "RAGAS evaluation executed successfully" | Out-File -FilePath $REPORT_FILE -Append
            Write-Host "RAGAS evaluation executed successfully"
        } else {
            "RAGAS evaluation failed" | Out-File -FilePath $REPORT_FILE -Append
            Write-Host "RAGAS evaluation failed"
            "Error: RAGAS evaluation script execution error" | Out-File -FilePath $REPORT_FILE -Append
            Write-Host "Error: RAGAS evaluation script execution error"
            "" | Out-File -FilePath $REPORT_FILE -Append
            "Test process terminated" | Out-File -FilePath $REPORT_FILE -Append
            Write-Host "Test process terminated"
            # Open report
            Write-Host "Opening test report..."
            Invoke-Item $REPORT_FILE
            exit 1
        }
    } catch {
        "RAGAS evaluation failed" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "RAGAS evaluation failed"
        "Error: RAGAS evaluation script execution error: $($_.Exception.Message)" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "Error: RAGAS evaluation script execution error: $($_.Exception.Message)"
        "" | Out-File -FilePath $REPORT_FILE -Append
        "Test process terminated" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "Test process terminated"
        # Open report
        Write-Host "Opening test report..."
        Invoke-Item $REPORT_FILE
        exit 1
    }
} else {
    "RAGAS evaluation failed" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "RAGAS evaluation failed"
    "Error: RAGAS evaluation script does not exist: $RAGAS_SCRIPT" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Error: RAGAS evaluation script does not exist: $RAGAS_SCRIPT"
    "" | Out-File -FilePath $REPORT_FILE -Append
    "Test process terminated" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Test process terminated"
    # Open report
    Write-Host "Opening test report..."
    Invoke-Item $REPORT_FILE
    exit 1
}

"" | Out-File -FilePath $REPORT_FILE -Append

# 3. DeepEval gate check (using system Python)
"[Step 3] DeepEval Gate Check" | Out-File -FilePath $REPORT_FILE -Append
"--------------------------------------------------------" | Out-File -FilePath $REPORT_FILE -Append

Write-Host "Executing DeepEval gate check..."
"Executing DeepEval gate check..." | Out-File -FilePath $REPORT_FILE -Append

if (Test-Path $DEEPEVAL_SCRIPT) {
    try {
        # Use system Python instead of virtual environment
        $output = & python $DEEPEVAL_SCRIPT 2>&1
        $output | Out-File -FilePath $REPORT_FILE -Append
        if ($LASTEXITCODE -eq 0) {
            "DeepEval gate check executed successfully" | Out-File -FilePath $REPORT_FILE -Append
            Write-Host "DeepEval gate check executed successfully"
        } else {
            "DeepEval gate check failed" | Out-File -FilePath $REPORT_FILE -Append
            Write-Host "DeepEval gate check failed"
            "Error: DeepEval gate script execution error" | Out-File -FilePath $REPORT_FILE -Append
            Write-Host "Error: DeepEval gate script execution error"
        }
    } catch {
        "DeepEval gate check failed" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "DeepEval gate check failed"
        "Error: DeepEval gate script execution error: $($_.Exception.Message)" | Out-File -FilePath $REPORT_FILE -Append
        Write-Host "Error: DeepEval gate script execution error: $($_.Exception.Message)"
    }
} else {
    "DeepEval gate check failed" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "DeepEval gate check failed"
    "Error: DeepEval gate script does not exist: $DEEPEVAL_SCRIPT" | Out-File -FilePath $REPORT_FILE -Append
    Write-Host "Error: DeepEval gate script does not exist: $DEEPEVAL_SCRIPT"
}

"" | Out-File -FilePath $REPORT_FILE -Append

# 4. Test report summary
"[Step 4] Test Report Summary" | Out-File -FilePath $REPORT_FILE -Append
"--------------------------------------------------------" | Out-File -FilePath $REPORT_FILE -Append
"Test process completed" | Out-File -FilePath $REPORT_FILE -Append
"Please see above output for detailed results" | Out-File -FilePath $REPORT_FILE -Append
"" | Out-File -FilePath $REPORT_FILE -Append
"========================================================" | Out-File -FilePath $REPORT_FILE -Append
"Test execution completed: $(Get-Date)" | Out-File -FilePath $REPORT_FILE -Append
"========================================================" | Out-File -FilePath $REPORT_FILE -Append

# Open test report
Write-Host "Opening test report..."
Invoke-Item $REPORT_FILE
