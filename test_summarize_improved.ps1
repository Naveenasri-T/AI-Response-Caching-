# Test improved summarization
Write-Host "=== Testing IMPROVED Summarization ===" -ForegroundColor Cyan
Write-Host ""

$text = "When a user asks a question in natural language, the backend sends it to a Large Language Model (LLM) that knows the database schema. The LLM generates an SQL query, which is validated and executed on the database. The results are then displayed back to the user through the user interface."

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"text`"$LF",
    $text,
    "--$boundary",
    "Content-Disposition: form-data; name=`"max_length`"$LF",
    "30",
    "--$boundary--$LF"
) -join $LF

Write-Host "Input text ($($text.Split().Count) words):" -ForegroundColor Yellow
Write-Host $text
Write-Host ""
Write-Host "Requesting summary with max 30 words..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/text/summarize" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines

    Write-Host ""
    Write-Host "Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
    Write-Host ""
    
    if ($response.summary) {
        Write-Host "Summary ($($response.summary_words) words):" -ForegroundColor Cyan
        Write-Host $response.summary
        Write-Host ""
        
        if ($response.summary_words -gt $response.original_words) {
            Write-Host "ERROR: Summary is LONGER than original!" -ForegroundColor Red
        } else {
            $saved = $response.original_words - $response.summary_words
            Write-Host "SUCCESS: Reduced by $saved words ($($response.compression_ratio)% compression)" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "Original: $($response.original_words) words | Summary: $($response.summary_words) words" -ForegroundColor Cyan
    Write-Host "Cache Hit: $($response.cache_hit)" -ForegroundColor $(if($response.cache_hit){"Green"}else{"Yellow"})
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2)) ms" -ForegroundColor Cyan
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
