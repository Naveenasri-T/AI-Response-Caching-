# Quick Image Endpoint Test
# Tests if the image models are working

$BASE_URL = "http://localhost:8000/api/v1"
$TEST_IMAGE_URL = "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400"  # Cat image

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Image Model Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Health Check First
Write-Host "[1/3] Checking API Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/health" -Method GET
    Write-Host "✅ API is running" -ForegroundColor Green
    Write-Host "Redis Connected: $($health.redis_connected)" -ForegroundColor Gray
    Write-Host "Memcached Connected: $($health.memcached_connected)" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "❌ API is not running. Please start the server first!" -ForegroundColor Red
    Write-Host "Run: uvicorn app.main:app --reload" -ForegroundColor Yellow
    exit 1
}

Start-Sleep -Seconds 1

# Test Image Captioning
Write-Host "[2/3] Testing Image Captioning..." -ForegroundColor Yellow
Write-Host "Model: nlpconnect/vit-gpt2-image-captioning" -ForegroundColor Gray
Write-Host "Image: Cat photo from Unsplash" -ForegroundColor Gray
Write-Host ""

$captionBody = @{
    image_url = $TEST_IMAGE_URL
}

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/image/caption" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $captionBody `
        -TimeoutSec 60
    
    Write-Host "✅ SUCCESS - Caption Generated!" -ForegroundColor Green
    Write-Host "Caption: $($response.caption)" -ForegroundColor White
    Write-Host "Model: $($response.model)" -ForegroundColor Gray
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2))ms" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "❌ FAILED - Captioning Error" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Detail: $($errorJson.detail)" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "⚠️ The model may be deprecated. Try alternative models:" -ForegroundColor Yellow
    Write-Host "  - Salesforce/blip-image-captioning-large" -ForegroundColor Gray
    Write-Host "  - microsoft/git-base" -ForegroundColor Gray
    Write-Host ""
}

Start-Sleep -Seconds 2

# Test Image Classification
Write-Host "[3/3] Testing Image Classification..." -ForegroundColor Yellow
Write-Host "Model: google/vit-base-patch16-224" -ForegroundColor Gray
Write-Host "Image: Cat photo from Unsplash" -ForegroundColor Gray
Write-Host ""

$classifyBody = @{
    image_url = $TEST_IMAGE_URL
    top_k = 3
}

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/image/classify" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $classifyBody `
        -TimeoutSec 60
    
    Write-Host "✅ SUCCESS - Image Classified!" -ForegroundColor Green
    Write-Host "Top Predictions:" -ForegroundColor White
    foreach ($pred in $response.predictions) {
        $score = [math]::Round($pred.score * 100, 2)
        Write-Host "  - $($pred.label): $score%" -ForegroundColor Cyan
    }
    Write-Host "Model: $($response.model)" -ForegroundColor Gray
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2))ms" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "❌ FAILED - Classification Error" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Detail: $($errorJson.detail)" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "⚠️ The model may be deprecated. Try alternative models:" -ForegroundColor Yellow
    Write-Host "  - facebook/convnext-tiny-224" -ForegroundColor Gray
    Write-Host "  - microsoft/swin-tiny-patch4-window7-224" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Test Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
