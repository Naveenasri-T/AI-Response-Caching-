# Test Image Endpoints - Comprehensive Testing Script
# This script tests both image classification and captioning with URLs and file uploads

$BASE_URL = "http://localhost:8000/api/v1"
$TEST_IMAGE_URL = "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400"  # Cat image
$TEST_IMAGE_DOG_URL = "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=400"  # Dog image

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Image Endpoints Testing Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Image Captioning with URL
Write-Host "[Test 1/4] Testing Image Captioning (URL)..." -ForegroundColor Yellow
Write-Host "Endpoint: POST $BASE_URL/image/caption" -ForegroundColor Gray
Write-Host "Image: Cat photo" -ForegroundColor Gray
Write-Host ""

$captionBody = @{
    image_url = $TEST_IMAGE_URL
}

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/image/caption" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $captionBody
    
    Write-Host "✅ SUCCESS - Caption Generated!" -ForegroundColor Green
    Write-Host "Caption: $($response.caption)" -ForegroundColor White
    Write-Host "Model: $($response.model)" -ForegroundColor Gray
    Write-Host "Cache Hit: $($response.cache_hit)" -ForegroundColor Gray
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2))ms" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "❌ FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

Start-Sleep -Seconds 2

# Test 2: Image Classification with URL
Write-Host "[Test 2/4] Testing Image Classification (URL)..." -ForegroundColor Yellow
Write-Host "Endpoint: POST $BASE_URL/image/classify" -ForegroundColor Gray
Write-Host "Image: Dog photo" -ForegroundColor Gray
Write-Host ""

$classifyBody = @{
    image_url = $TEST_IMAGE_DOG_URL
    top_k = 5
}

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/image/classify" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $classifyBody
    
    Write-Host "✅ SUCCESS - Image Classified!" -ForegroundColor Green
    Write-Host "Top Predictions:" -ForegroundColor White
    foreach ($pred in $response.predictions) {
        $score = [math]::Round($pred.score * 100, 2)
        Write-Host "  - $($pred.label): $score%" -ForegroundColor Cyan
    }
    Write-Host "Model: $($response.model)" -ForegroundColor Gray
    Write-Host "Cache Hit: $($response.cache_hit)" -ForegroundColor Gray
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2))ms" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "❌ FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

Start-Sleep -Seconds 2

# Test 3: Caption with Cache Hit (repeat Test 1)
Write-Host "[Test 3/4] Testing Cache Hit (Caption)..." -ForegroundColor Yellow
Write-Host "Repeating same request to test caching" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/image/caption" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $captionBody
    
    if ($response.cache_hit -eq $true) {
        Write-Host "✅ SUCCESS - Cache Working!" -ForegroundColor Green
        Write-Host "Cache Source: $($response.cache_source)" -ForegroundColor Cyan
        Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2))ms (from cache)" -ForegroundColor Cyan
        Write-Host "Caption: $($response.caption)" -ForegroundColor White
    }
    else {
        Write-Host "⚠️ WARNING - Cache Miss (Expected Hit)" -ForegroundColor Yellow
        Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2))ms" -ForegroundColor Gray
    }
    Write-Host ""
}
catch {
    Write-Host "❌ FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Start-Sleep -Seconds 2

# Test 4: Download test image for file upload test
Write-Host "[Test 4/4] Testing Image Upload Endpoints..." -ForegroundColor Yellow
Write-Host "Downloading test image..." -ForegroundColor Gray

$testImagePath = "$env:TEMP\test_cat.jpg"

try {
    # Download test image
    Invoke-WebRequest -Uri $TEST_IMAGE_URL -OutFile $testImagePath
    Write-Host "✅ Test image downloaded to: $testImagePath" -ForegroundColor Green
    Write-Host ""
    
    # Test image upload classification
    Write-Host "Testing: POST $BASE_URL/image/upload/classify" -ForegroundColor Gray
    
    $form = @{
        image = Get-Item -Path $testImagePath
        top_k = 3
    }
    
    $response = Invoke-RestMethod -Uri "$BASE_URL/image/upload/classify" `
        -Method POST `
        -Form $form
    
    Write-Host "✅ SUCCESS - Upload Classification!" -ForegroundColor Green
    Write-Host "Filename: $($response.filename)" -ForegroundColor White
    Write-Host "Size: $($response.size_bytes) bytes" -ForegroundColor Gray
    Write-Host "Top Predictions:" -ForegroundColor White
    foreach ($pred in $response.predictions) {
        $score = [math]::Round($pred.score * 100, 2)
        Write-Host "  - $($pred.label): $score%" -ForegroundColor Cyan
    }
    Write-Host "Response Time: $([math]::Round($response.response_time_ms, 2))ms" -ForegroundColor Gray
    Write-Host ""
    
    # Test image upload captioning
    Write-Host "Testing: POST $BASE_URL/image/upload/caption" -ForegroundColor Gray
    
    $form2 = @{
        image = Get-Item -Path $testImagePath
    }
    
    $response2 = Invoke-RestMethod -Uri "$BASE_URL/image/upload/caption" `
        -Method POST `
        -Form $form2
    
    Write-Host "✅ SUCCESS - Upload Captioning!" -ForegroundColor Green
    Write-Host "Caption: $($response2.caption)" -ForegroundColor White
    Write-Host "Response Time: $([math]::Round($response2.response_time_ms, 2))ms" -ForegroundColor Gray
    Write-Host ""
    
    # Cleanup
    Remove-Item -Path $testImagePath -Force
    Write-Host "Cleaned up test image" -ForegroundColor Gray
}
catch {
    Write-Host "❌ FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Image Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "  - First requests will be slower (model loading)" -ForegroundColor Gray
Write-Host "  - Repeated requests should be much faster (cache)" -ForegroundColor Gray
Write-Host "  - Check statistics at: $BASE_URL/statistics" -ForegroundColor Gray
Write-Host ""
