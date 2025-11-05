# Test image classification with new model
Write-Host "=== Testing Image Classification with microsoft/resnet-50 ===" -ForegroundColor Cyan
Write-Host ""

$imageUrl = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/beignets-task-guide.png"

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"image_url`"$LF",
    $imageUrl,
    "--$boundary",
    "Content-Disposition: form-data; name=`"top_k`"$LF",
    "5",
    "--$boundary--$LF"
) -join $LF

Write-Host "Image URL: $imageUrl" -ForegroundColor Yellow
Write-Host "Requesting top 5 classifications..." -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/image/classify" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines

    Write-Host "Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
    Write-Host ""
    
    if ($response.predictions) {
        Write-Host "Top Predictions:" -ForegroundColor Cyan
        $response.predictions | ForEach-Object {
            Write-Host "  - $($_.label): $([math]::Round($_.score * 100, 2))%"
        }
    }
    
    Write-Host ""
    Write-Host "Model: $($response.model)" -ForegroundColor Cyan
    Write-Host "Cache Hit: $($response.cache_hit)" -ForegroundColor $(if($response.cache_hit){"Green"}else{"Yellow"})
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2)) ms" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "SUCCESS! New model (microsoft/resnet-50) is working!" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}
