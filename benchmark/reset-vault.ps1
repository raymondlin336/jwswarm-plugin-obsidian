# Restores the live benchmark vault to match vault-template.
# Only touches files that differ, so unchanged notes don't add Sync or File Recovery versions.
param(
    # Outside the repo, so agents under test can't reach the plugin's files from the vault.
    [string]$VaultPath = (Join-Path $env:USERPROFILE 'obsidian-bench\vault3')
)

$ErrorActionPreference = 'Stop'
$template = Join-Path $PSScriptRoot 'vault-template'
$appDataFolder = '.obsidian'

if ((Test-Path $VaultPath) -and -not (Test-Path (Join-Path $VaultPath '.jw-benchmark-vault'))) {
    throw "$VaultPath exists but is not a benchmark vault. Refusing to change it."
}
New-Item -ItemType Directory -Force $VaultPath | Out-Null
New-Item -ItemType File -Force (Join-Path $VaultPath '.jw-benchmark-vault') | Out-Null

function Get-RelativePath($root, $path) {
    $path.Substring($root.TrimEnd('\').Length + 1)
}

$templateFiles = @{}
Get-ChildItem $template -Recurse -File -Force | ForEach-Object {
    $templateFiles[(Get-RelativePath $template $_.FullName)] = $_.FullName
}

$changed = @()
foreach ($relative in $templateFiles.Keys) {
    $target = Join-Path $VaultPath $relative
    $source = $templateFiles[$relative]
    if ((Test-Path -LiteralPath $target) -and
        (Get-FileHash -LiteralPath $target).Hash -eq (Get-FileHash -LiteralPath $source).Hash) {
        continue
    }
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Force
    $changed += "restored  $relative"
}

# Remove anything an agent added. Obsidian's own app files in .obsidian are left alone.
$root = (Resolve-Path $VaultPath).Path
Get-ChildItem $root -Recurse -File -Force | ForEach-Object {
    $relative = Get-RelativePath $root $_.FullName
    if ($relative -eq '.jw-benchmark-vault' -or $relative.StartsWith("$appDataFolder\")) { return }
    if (-not $templateFiles.ContainsKey($relative)) {
        # The extended path prefix also deletes files with reserved names, like "nul" left by a shell redirect.
        [IO.File]::Delete('\\?\' + $_.FullName)
        $changed += "removed   $relative"
    }
}
Get-ChildItem $root -Recurse -Directory -Force |
    Where-Object { $_.FullName -notlike "$root\$appDataFolder*" } |
    Sort-Object { $_.FullName.Length } -Descending |
    Where-Object { -not (Get-ChildItem -LiteralPath $_.FullName -Force) } |
    ForEach-Object {
        Remove-Item -LiteralPath $_.FullName -Force
        $changed += "removed   $(Get-RelativePath $root $_.FullName)\"
    }

if ($changed.Count -eq 0) {
    Write-Output 'Vault already matches the template.'
} else {
    $changed | Sort-Object | ForEach-Object { Write-Output $_ }
}
if ($changed -match [regex]::Escape("$appDataFolder\")) {
    Write-Output 'Settings changed: restart Obsidian so it loads them.'
}
