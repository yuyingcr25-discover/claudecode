# PowerShell script to sideload Excel add-in
$manifestPath = "c:\Users\Yuying Chen-Wynn\Documents\GitHub\claudecode\manifest.xml"

Write-Host "Attempting to sideload Excel add-in..." -ForegroundColor Green

# Method 1: Copy to user's add-in folder
$addinFolder = "$env:LOCALAPPDATA\Microsoft\Office\16.0\Wef"
if (-not (Test-Path $addinFolder)) {
    New-Item -Path $addinFolder -ItemType Directory -Force | Out-Null
}
Copy-Item $manifestPath -Destination "$addinFolder\manifest_project_setup.xml" -Force
Write-Host "Copied manifest to: $addinFolder" -ForegroundColor Yellow

# Method 2: Try Office.js debugging tool
Write-Host "`nAttempting to open Excel with add-in..." -ForegroundColor Green
try {
    # Find Excel executable
    $excelPath = "C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"
    if (-not (Test-Path $excelPath)) {
        $excelPath = "C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE"
    }

    if (Test-Path $excelPath) {
        Write-Host "Found Excel at: $excelPath" -ForegroundColor Cyan
        Write-Host "`nInstructions:" -ForegroundColor Yellow
        Write-Host "1. Excel will open in a moment"
        Write-Host "2. Go to Insert tab > Add-ins (or Office Add-ins)"
        Write-Host "3. Look for 'MY ADD-INS' tab"
        Write-Host "4. Find 'Project Setup Tools' and click to load it"
        Write-Host "`nPress any key to open Excel..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Start-Process $excelPath
    } else {
        Write-Host "Could not find Excel executable" -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`nManifest location: $manifestPath" -ForegroundColor Cyan
Write-Host "Dev server should be running at: https://localhost:3000" -ForegroundColor Cyan
