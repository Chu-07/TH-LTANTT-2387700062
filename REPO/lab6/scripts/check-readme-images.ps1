[CmdletBinding()]
param(
    [string]$ReadmePath = (Join-Path $PSScriptRoot '..\README.md')
)

$readme = Get-Item -LiteralPath $ReadmePath -ErrorAction Stop
$content = Get-Content -LiteralPath $readme.FullName -Raw -Encoding UTF8
$pattern = '!\[[^\]]*\]\((?:<)?(?<path>[^)>]+)(?:>)?\)'
$matches = [regex]::Matches($content, $pattern)
$missing = @()

foreach ($match in $matches) {
    $relativePath = [uri]::UnescapeDataString($match.Groups['path'].Value)
    if ($relativePath -match '^[a-zA-Z][a-zA-Z0-9+.-]*://') {
        continue
    }

    $resolvedPath = Join-Path $readme.DirectoryName $relativePath
    if (-not (Test-Path -LiteralPath $resolvedPath -PathType Leaf)) {
        $missing += $relativePath
    }
}

Write-Host "Markdown images: $($matches.Count)"
Write-Host "Missing local images: $($missing.Count)"

if ($missing.Count -gt 0) {
    $missing | ForEach-Object { Write-Error "Missing image: $_" }
    exit 1
}

Write-Host 'All local image links are valid.'
