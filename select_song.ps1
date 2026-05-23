param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir
)

$supportedExtensions = @(
    ".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".aiff"
)

if (-not (Test-Path -LiteralPath $SourceDir -PathType Container)) {
    Write-Host ""
    Write-Host "Source folder not found: $SourceDir" -ForegroundColor Red
    exit 3
}

$files = Get-ChildItem -LiteralPath $SourceDir -File |
    Where-Object { $supportedExtensions -contains $_.Extension.ToLowerInvariant() } |
    Sort-Object Name

if (-not $files) {
    Write-Host ""
    Write-Host "No supported audio files were found in original_songs." -ForegroundColor Yellow
    exit 3
}

$selectedIndex = 0
$topIndex = 0
$windowHeight = $Host.UI.RawUI.WindowSize.Height
$visibleCount = [Math]::Min([Math]::Max($windowHeight - 8, 5), $files.Count)

function Show-Menu {
    param(
        [System.IO.FileInfo[]]$Items,
        [int]$CurrentIndex,
        [int]$StartIndex,
        [int]$PageSize
    )

    Clear-Host
    Write-Host ""
    Write-Host "========================================================"
    Write-Host " Select a song to process"
    Write-Host "========================================================"
    Write-Host ""
    Write-Host "Use Up/Down to move, Enter to confirm, Esc to cancel"
    Write-Host ""

    $endIndex = [Math]::Min($StartIndex + $PageSize - 1, $Items.Count - 1)
    for ($i = $StartIndex; $i -le $endIndex; $i++) {
        if ($i -eq $CurrentIndex) {
            Write-Host ("> " + $Items[$i].Name) -ForegroundColor Cyan
        } else {
            Write-Host ("  " + $Items[$i].Name)
        }
    }

    Write-Host ""
    Write-Host ("Song {0} / {1}" -f ($CurrentIndex + 1), $Items.Count) -ForegroundColor DarkGray
}

while ($true) {
    if ($selectedIndex -lt $topIndex) {
        $topIndex = $selectedIndex
    }

    if ($selectedIndex -ge ($topIndex + $visibleCount)) {
        $topIndex = $selectedIndex - $visibleCount + 1
    }

    Show-Menu -Items $files -CurrentIndex $selectedIndex -StartIndex $topIndex -PageSize $visibleCount
    $key = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

    switch ($key.VirtualKeyCode) {
        13 {
            Write-Output $files[$selectedIndex].FullName
            exit 0
        }
        27 {
            exit 2
        }
        38 {
            if ($selectedIndex -gt 0) {
                $selectedIndex--
            } else {
                $selectedIndex = $files.Count - 1
            }
        }
        40 {
            if ($selectedIndex -lt ($files.Count - 1)) {
                $selectedIndex++
            } else {
                $selectedIndex = 0
            }
        }
        33 {
            $selectedIndex = [Math]::Max($selectedIndex - $visibleCount, 0)
        }
        34 {
            $selectedIndex = [Math]::Min($selectedIndex + $visibleCount, $files.Count - 1)
        }
        36 {
            $selectedIndex = 0
        }
        35 {
            $selectedIndex = $files.Count - 1
        }
    }
}
