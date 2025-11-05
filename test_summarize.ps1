# Test summarization endpoint
Write-Host "=== Testing Summarization ===" -ForegroundColor Cyan
Write-Host ""

$text = "This boilerplate is designed to convert natural language inputs (like user questions) into SQL queries and fetch results from a structured database. It already has logic for Text-to-SQL, database connectivity, and a user interface for chat interaction."

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"text`"$LF",
    $text,
    "--$boundary",
    "Content-Disposition: form-data; name=`"max_length`"$LF",
    "50",
    "--$boundary--$LF"
) -join $LF

Write-Host "Input text:" -ForegroundColor Yellow
Write-Host $text
Write-Host ""
Write-Host "Calling API..." -ForegroundColor Yellow

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
        Write-Host "Summary:" -ForegroundColor Cyan
        Write-Host $response.summary
    }
    
    Write-Host ""
    Write-Host "Cache Hit: $($response.cache_hit)" -ForegroundColor $(if($response.cache_hit){"Green"}else{"Yellow"})
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2)) ms" -ForegroundColor Cyan
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
