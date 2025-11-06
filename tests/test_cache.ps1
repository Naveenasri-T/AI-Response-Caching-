# Test caching behavior
Write-Host "=== Testing Cache Behavior ===" -ForegroundColor Cyan
Write-Host ""

# Create multipart form data
$text = "Naveenasri"
$target_language = "Tamil"

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"text`"$LF",
    $text,
    "--$boundary",
    "Content-Disposition: form-data; name=`"target_language`"$LF",
    $target_language,
    "--$boundary--$LF"
) -join $LF

# First request (should be MISS)
Write-Host "First Request (expecting cache MISS)..." -ForegroundColor Yellow
$response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/text/translate" `
    -Method Post `
    -ContentType "multipart/form-data; boundary=$boundary" `
    -Body $bodyLines

Write-Host "Response:" -ForegroundColor Green
$response1 | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "Cache Hit: $($response1.cache_hit)" -ForegroundColor $(if($response1.cache_hit){"Green"}else{"Red"})
Write-Host "Cache Source: $($response1.cache_source)" -ForegroundColor Cyan
Write-Host "Response Time: $([math]::Round($response1.response_time_ms, 2)) ms" -ForegroundColor Cyan
Write-Host ""

# Wait a moment
Start-Sleep -Seconds 2

# Second request (should be HIT)
Write-Host "Second Request (expecting cache HIT)..." -ForegroundColor Yellow
$response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/text/translate" `
    -Method Post `
    -ContentType "multipart/form-data; boundary=$boundary" `
    -Body $bodyLines

Write-Host "Response:" -ForegroundColor Green
$response2 | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "Cache Hit: $($response2.cache_hit)" -ForegroundColor $(if($response2.cache_hit){"Green"}else{"Red"})
Write-Host "Cache Source: $($response2.cache_source)" -ForegroundColor Cyan
Write-Host "Response Time: $([math]::Round($response2.response_time_ms, 2)) ms" -ForegroundColor Cyan
Write-Host ""

# Compare
Write-Host "=== Comparison ===" -ForegroundColor Cyan
Write-Host "First request:  cache_hit=$($response1.cache_hit), source=$($response1.cache_source), time=$([math]::Round($response1.response_time_ms, 2))ms"
Write-Host "Second request: cache_hit=$($response2.cache_hit), source=$($response2.cache_source), time=$([math]::Round($response2.response_time_ms, 2))ms"
Write-Host ""

if ($response2.cache_hit) {
    $speedup = [math]::Round($response1.response_time_ms / $response2.response_time_ms, 2)
    Write-Host "SUCCESS! Cache is working! Second request was $speedup times faster!" -ForegroundColor Green
} else {
    Write-Host "WARNING: Second request was not cached. Check logs." -ForegroundColor Red
}
