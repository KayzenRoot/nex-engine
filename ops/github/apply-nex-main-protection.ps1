#Requires -Version 5.1
<#
NEX Engine | apply main Ruleset with gh CLI on authorized Codex Desktop Windows.
Dry-run by default. -Apply requires PR #72 merged and checks verified.
Never provide PAT/secrets to scripts or assistant. Do not run without owner access.
#>
param([switch]$Apply)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='KayzenRoot/nex-engine'
$targetName='NEX | main protected quality gates'
$policy=Join-Path $PSScriptRoot 'nex-main-ruleset.json'

function GhJson([string[]]$ArgsForGh) {
  $out = & gh @ArgsForGh 2>&1
  if ($LASTEXITCODE -ne 0) { throw "GitHub API request failed: $($ArgsForGh -join ' ') - $($out | Out-String)" }
  $s = ($out | Out-String).Trim()
  if (-not $s) { throw "Empty API result for $($ArgsForGh -join ' ')" }
  return ($s | ConvertFrom-Json)
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'Missing gh. Install GitHub CLI and sign in interactively; never paste access tokens into logs.' }
& gh auth status --hostname github.com 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'GH auth is not ready. Use gh auth login yourself in local terminal and retry.' }
$repoInfo=GhJson @('api',"repos/$repo")
if ($repoInfo.full_name -cne $repo -or $repoInfo.default_branch -cne 'main') { throw 'Unexpected GitHub repository or default branch.' }
if (-not (Test-Path -LiteralPath $policy -PathType Leaf)) { throw 'Missing ruleset JSON.' }
$desired=Get-Content -LiteralPath $policy -Raw | ConvertFrom-Json
if ($desired.enforcement -ne 'active' -or $desired.target -ne 'branch') { throw 'Unexpected desired ruleset.' }
$ruleList=@(GhJson @('api',"repos/$repo/rulesets"))
$matches=@($ruleList | Where-Object { $_.name -eq $targetName })
if ($matches.Count -gt 1) { throw 'More than one ruleset with this name. STOP.' }
$pr=GhJson @('api',"repos/$repo/pulls/72")
$sha=$pr.head.sha
Write-Host "NEX status: PR #72 merged=$($pr.merged), historical head=$sha"
Write-Host "Matching main rulesets=$($matches.Count)"
if (-not $Apply) { Write-Host 'DRY RUN only. PR #72 must pass and merge before applying -Apply.'; exit 0 }
if (-not $pr.merged) { throw 'PR #72 not merged. Do not bypass pending CodeRabbit or merge gates.' }
$status=GhJson @('api',"repos/$repo/commits/$sha/status")
$rabbit=@($status.statuses | Where-Object { $_.context -eq 'CodeRabbit' -and $_.state -eq 'success' })
if ($rabbit.Count -lt 1) { throw 'CodeRabbit on PR #72 HEAD was not SUCCESS.' }
$checkruns=GhJson @('api',"repos/$repo/commits/$sha/check-runs?per_page=100")
foreach($name in @('Socket Security: Pull Request Alerts','Socket Security: Project Report')) {
  $valid=@($checkruns.check_runs | Where-Object { $_.name -eq $name -and $_.status -eq 'completed' -and $_.conclusion -eq 'success' })
  if ($valid.Count -eq 0) { throw "Missing historical green check: $name" }
}
$temp=Join-Path ([System.IO.Path]::GetTempPath()) ('nex-rules-'+[guid]::NewGuid().ToString('N')+'.json')
$settingsTemp=Join-Path ([System.IO.Path]::GetTempPath()) ('nex-settings-'+[guid]::NewGuid().ToString('N')+'.json')
try {
  $encoding=New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($temp,(Get-Content -LiteralPath $policy -Raw),$encoding)
  $repoSettings=@{ allow_squash_merge=$true; allow_merge_commit=$false; allow_rebase_merge=$false; allow_auto_merge=$true; delete_branch_on_merge=$true }
  [System.IO.File]::WriteAllText($settingsTemp,($repoSettings | ConvertTo-Json -Depth 8),$encoding)
  $null=GhJson @('api','--method','PATCH',"repos/$repo",'--input',$settingsTemp)
  if ($matches.Count -eq 1) {
    $rulesetId=[int]$matches[0].id
    $null=GhJson @('api','--method','PUT',"repos/$repo/rulesets/$rulesetId",'--input',$temp)
  } else {
    $created=GhJson @('api','--method','POST',"repos/$repo/rulesets",'--input',$temp)
    $rulesetId=[int]$created.id
  }
  $actual=GhJson @('api',"repos/$repo/rulesets/$rulesetId")
  if ($actual.enforcement -ne 'active' -or $actual.target -ne 'branch') { throw 'Ruleset not active after write.' }
  $ruleTypes=@($actual.rules | ForEach-Object { $_.type })
  foreach($name in @('deletion','non_fast_forward','required_linear_history','pull_request','required_status_checks')) {
    if ($ruleTypes -notcontains $name) { throw "Missing protection: $name" }
  }
  $pull=@($actual.rules | Where-Object { $_.type -eq 'pull_request' })[0]
  if ($pull.parameters.required_approving_review_count -ne 0 -or -not $pull.parameters.required_review_thread_resolution) { throw 'PR policy mismatch.' }
  $statusRule=@($actual.rules | Where-Object { $_.type -eq 'required_status_checks' })[0]
  if (-not $statusRule.parameters.strict_required_status_checks_policy) { throw 'Strict checks not enabled.' }
  $contexts=@($statusRule.parameters.required_status_checks | ForEach-Object { $_.context })
  foreach($name in @('CodeRabbit','Socket Security: Pull Request Alerts','Socket Security: Project Report')) {
    if ($contexts -notcontains $name) { throw "Required check absent: $name" }
  }
  $settings=GhJson @('api',"repos/$repo")
  if ($settings.allow_merge_commit -or $settings.allow_rebase_merge -or -not $settings.allow_squash_merge) { throw 'Squash-only repo settings mismatch.' }
  Write-Host "VERIFIED: ACTIVE main ruleset $rulesetId, checks, PR, threads, squash-only, no force or delete."
  Write-Host 'Require GEF Smoke CI jobs later ONLY after they exist and have passed on real PR HEAD.'
} finally {
  Remove-Item -LiteralPath $temp,$settingsTemp -Force -ErrorAction SilentlyContinue
}
