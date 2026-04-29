param(
    [string]$Source = "assets/img/journeys",
    [string]$Output = "assets/js/journeys-data.js",
    [string]$ThumbnailDestination = "assets/img/journeys-thumbs",
    [string]$WebDestination = "assets/img/journeys-web",
    [int]$ThumbnailMaxSize = 640,
    [int]$ThumbnailQuality = 72,
    [int]$WebMaxSize = 1800,
    [int]$WebQuality = 82
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $Source).Path
$workspaceRoot = (Get-Location).Path
$workspaceUri = [System.Uri]::new(($workspaceRoot.TrimEnd("\") + "\"))
$imageExtensions = @(".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
$thumbnailRoot = Join-Path $workspaceRoot $ThumbnailDestination
$webRoot = Join-Path $workspaceRoot $WebDestination
New-Item -ItemType Directory -Path $thumbnailRoot -Force | Out-Null
New-Item -ItemType Directory -Path $webRoot -Force | Out-Null
Add-Type -AssemblyName System.Drawing

function Convert-ToRelativeWebPath([string]$path) {
    $fileUri = [System.Uri]::new($path)
    $relativeUri = $workspaceUri.MakeRelativeUri($fileUri).ToString()
    [System.Uri]::UnescapeDataString($relativeUri)
}

function Get-AlbumId([string]$name) {
    ($name.ToLowerInvariant() -replace "[^a-z0-9]+", "-" -replace "^-|-$", "")
}

function Get-FileSlug([string]$name) {
    $slug = ([System.IO.Path]::GetFileNameWithoutExtension($name).ToLowerInvariant() -replace "[^a-z0-9]+", "-" -replace "^-|-$", "")
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return "photo"
    }
    return $slug
}

function Convert-ToTitle([string]$name) {
    $text = $name -replace "[-_]+", " "
    $text = $text -replace "\s+", " "
    $text = $text.Trim()

    $special = @{
        "washington dc" = "Washington DC"
        "upper peninsula" = "Upper Peninsula"
        "pennsilvenia" = "Pennsylvania"
    }

    $lower = $text.ToLowerInvariant()
    if ($special.ContainsKey($lower)) {
        return $special[$lower]
    }

    $culture = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
    return $culture.TextInfo.ToTitleCase($lower)
}

function Set-ImageOrientation([System.Drawing.Image]$image) {
    $orientationId = 0x0112
    if (-not ($image.PropertyIdList -contains $orientationId)) {
        return
    }

    $orientation = [BitConverter]::ToUInt16($image.GetPropertyItem($orientationId).Value, 0)
    switch ($orientation) {
        2 { $image.RotateFlip([System.Drawing.RotateFlipType]::RotateNoneFlipX) }
        3 { $image.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipNone) }
        4 { $image.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipX) }
        5 { $image.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipX) }
        6 { $image.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipNone) }
        7 { $image.RotateFlip([System.Drawing.RotateFlipType]::Rotate270FlipX) }
        8 { $image.RotateFlip([System.Drawing.RotateFlipType]::Rotate270FlipNone) }
    }
}

function New-ResizedJpeg([string]$sourceImage, [string]$outputPath, [int]$maxSize, [int]$quality) {
    if ((Test-Path -LiteralPath $outputPath) -and ((Get-Item -LiteralPath $outputPath).LastWriteTimeUtc -ge (Get-Item -LiteralPath $sourceImage).LastWriteTimeUtc)) {
        return $outputPath
    }

    New-Item -ItemType Directory -Path (Split-Path -Path $outputPath -Parent) -Force | Out-Null

    $image = $null
    $resized = $null
    $graphics = $null

    try {
        $image = [System.Drawing.Image]::FromFile($sourceImage)
        Set-ImageOrientation $image

        $ratio = [Math]::Min($maxSize / $image.Width, $maxSize / $image.Height)
        $ratio = [Math]::Min($ratio, 1)
        $width = [Math]::Max(1, [int]($image.Width * $ratio))
        $height = [Math]::Max(1, [int]($image.Height * $ratio))

        $resized = New-Object System.Drawing.Bitmap($width, $height)
        $graphics = [System.Drawing.Graphics]::FromImage($resized)
        $graphics.Clear([System.Drawing.Color]::White)
        $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
        $graphics.DrawImage($image, 0, 0, $width, $height)

        $encoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
        $encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
        $encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter([System.Drawing.Imaging.Encoder]::Quality, [int64]$quality)
        $resized.Save($outputPath, $encoder, $encoderParams)
        return $outputPath
    }
    catch {
        Write-Warning "Could not create web image for '$sourceImage': $($_.Exception.Message)"
        return $sourceImage
    }
    finally {
        if ($graphics) { $graphics.Dispose() }
        if ($resized) { $resized.Dispose() }
        if ($image) { $image.Dispose() }
    }
}

function New-JourneyThumbnail([string]$sourceImage, [string]$albumId) {
    $outputPath = Join-Path $thumbnailRoot "$albumId.jpg"
    return New-ResizedJpeg $sourceImage $outputPath $ThumbnailMaxSize $ThumbnailQuality
}

function New-JourneyWebPhoto([string]$sourceImage, [string]$albumId, [int]$index) {
    $sourceName = [System.IO.Path]::GetFileName($sourceImage)
    $fileSlug = Get-FileSlug $sourceName
    $albumRoot = Join-Path $webRoot $albumId
    $outputPath = Join-Path $albumRoot ("{0:D3}-{1}.jpg" -f $index, $fileSlug)
    return New-ResizedJpeg $sourceImage $outputPath $WebMaxSize $WebQuality
}

$albums = Get-ChildItem -LiteralPath $root -Directory |
    Sort-Object Name |
    ForEach-Object {
        $folder = $_
        $albumId = Get-AlbumId $folder.Name
        $imageFiles = @(Get-ChildItem -LiteralPath $folder.FullName -File |
            Where-Object { $imageExtensions -contains $_.Extension.ToLowerInvariant() } |
            Sort-Object Name)

        if ($imageFiles.Count -eq 0) {
            return
        }

        $photoIndex = 0
        $images = $imageFiles | ForEach-Object {
            $photoIndex += 1
            $webPhoto = New-JourneyWebPhoto $_.FullName $albumId $photoIndex
            Convert-ToRelativeWebPath $webPhoto
        }
        $thumbnailPath = New-JourneyThumbnail $imageFiles[0].FullName $albumId

        [ordered]@{
            id = $albumId
            title = Convert-ToTitle $folder.Name
            cover = Convert-ToRelativeWebPath $thumbnailPath
            photos = @($images)
        }
    }

$json = $albums | ConvertTo-Json -Depth 6
$content = "window.JOURNEY_ALBUMS = $json;`n"

$outputPath = Join-Path (Get-Location).Path $Output
New-Item -ItemType Directory -Path (Split-Path -Path $outputPath -Parent) -Force | Out-Null
Set-Content -LiteralPath $outputPath -Value $content -Encoding UTF8

Write-Host "Updated $Output"
Write-Host "Albums: $($albums.Count)"
