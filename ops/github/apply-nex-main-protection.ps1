#Requires -Version 5.1
<#
NEX Engine | apply main Ruleset with gh CLI on authorized Codex Desktop Windows.
Dry-run by default. -Apply requires PRs #72 and #73 merged after exact-head checks and Owner/Steward audit.
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

function AssertLatestStatusSuccess([object[]]$Statuses, [string]$Context) {
  $candidates=@($Statuses | Where-Object { $_.context -eq $Context } | Sort-Object -Property @{Expression={ [DateTimeOffset]$_.created_at }; Descending=$true})
  if ($candidates.Count -eq 0) { throw "Missing required status on exact HEAD: $Context" }
  $latest=$candidates[0]
  if ($latest.state -ne 'success') { throw "Latest status on exact HEAD is not SUCCESS: $Context (state=$($latest.state), created_at=$($latest.created_at))" }
}

function AssertLatestCheckRunSuccess([object[]]$CheckRuns, [string]$Name) {
  $candidates=@($CheckRuns | Where-Object { $_.name -eq $Name } | Sort-Object -Property @{Expression={ [DateTimeOffset]$_.created_at }; Descending=$true}, @{Expression={ [int]$_.run_attempt }; Descending=$true})
  if ($candidates.Count -eq 0) { throw "Missing required check on exact HEAD: $Name" }
  $latest=$candidates[0]
  if ($latest.status -ne 'completed' -or $latest.conclusion -ne 'success') {
    throw "Latest check on exact HEAD is not SUCCESS: $Name (status=$($latest.status), conclusion=$($latest.conclusion), created_at=$($latest.created_at))"
  }
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
if (-not $Apply) { Write-Host 'DRY RUN only. PRs #72 and #73 must pass their exact-head checks, receive Owner/Steward audit, and merge before -Apply.'; exit 0 }
if (-not $pr.merged) { throw 'PR #72 not merged. Do not bypass pending CodeRabbit or merge gates.' }
$status=GhJson @('api',"repos/$repo/commits/$sha/status")
AssertLatestStatusSuccess -Statuses @($status.statuses) -Context 'CodeRabbit'
$checkruns=GhJson @('api',"repos/$repo/commits/$sha/check-runs?per_page=100")
foreach($name in @('Socket Security: Pull Request Alerts','Socket Security: Project Report')) {
  AssertLatestCheckRunSuccess -CheckRuns @($checkruns.check_runs) -Name $name
}
# Do not activate a branch ruleset from unmerged or unreviewed configuration.
$opsPr=GhJson @('api',"repos/$repo/pulls/73")
if (-not $opsPr.merged) { throw 'PR #73 must pass Owner/Steward audit and merge before -Apply.' }
$opsSha=$opsPr.head.sha
$opsStatus=GhJson @('api',"repos/$repo/commits/$opsSha/status")
AssertLatestStatusSuccess -Statuses @($opsStatus.statuses) -Context 'CodeRabbit'
$opsChecks=GhJson @('api',"repos/$repo/commits/$opsSha/check-runs?per_page=100")
foreach($needed in @('Socket Security: Pull Request Alerts','Socket Security: Project Report','NEX Governance / Source Pack','NEX Governance / PowerShell')) {
  AssertLatestCheckRunSuccess -CheckRuns @($opsChecks.check_runs) -Name $needed
}
$temp=Join-Path ([System.IO.Path]::GetTempPath()) ('nex-rules-'+[guid]::NewGuid().ToString('N')+'.json')
$settingsTemp=Join-Path ([System.IO.Path]::GetTempPath()) ('nex-settings-'+[guid]::NewGuid().ToString('N')+'.json')
try {
  $encoding=New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($temp,(Get-Content -LiteralPath $policy -Raw),$encoding)
  $repoSettings=@{ allow_squash_merge=$true; allow_merge_commit=$false; allow_rebase_merge=$false; allow_auto_merge=$true; delete_branch_on_merge=$true }
  [System.IO.File]::WriteAllText($settingsTemp,($repoSettings | ConvertTo-Json -Depth 8),$encoding)
  if ($matches.Count -eq 1) {
    $rulesetId=[int]$matches[0].id
    $null=GhJson @('api','--method','PUT',"repos/$repo/rulesets/$rulesetId",'--input',$temp)
  } else {
    $created=GhJson @('api','--method','POST',"repos/$repo/rulesets",'--input',$temp)
    $rulesetId=[int]$created.id
  }
  $actual=GhJson @('api',"repos/$repo/rulesets/$rulesetId")
  if ($actual.enforcement -ne 'active' -or $actual.target -ne 'branch') { throw 'Ruleset not active after write.' }
  if ($actual.name -cne $targetName) { throw 'Unexpected Ruleset name after write.' }
  $includes=@($actual.conditions.ref_name.include)
  $excludes=@($actual.conditions.ref_name.exclude | Where-Object { $_ })
  if ($includes.Count -ne 1 -or $includes[0] -cne '~DEFAULT_BRANCH' -or $excludes.Count -ne 0) { throw 'Ruleset does not target only the default branch.' }
  if (@($actual.bypass_actors | Where-Object { $_ }).Count -ne 0) { throw 'Ruleset bypass actors must remain empty.' }
  $ruleTypes=@($actual.rules | ForEach-Object { $_.type })
  $expectedRuleTypes=@($desired.rules | ForEach-Object { $_.type } | Sort-Object -CaseSensitive)
  $actualRuleTypes=@($ruleTypes | Sort-Object -CaseSensitive)
  if ($actualRuleTypes.Count -ne $expectedRuleTypes.Count -or ($actualRuleTypes -join "`n") -cne ($expectedRuleTypes -join "`n")) { throw 'Ruleset rule types do not exactly match the approved set.' }
  foreach($name in @('deletion','non_fast_forward','required_linear_history','pull_request','required_status_checks')) {
    if ($ruleTypes -notcontains $name) { throw "Missing protection: $name" }
  }
  $pull=@($actual.rules | Where-Object { $_.type -eq 'pull_request' })[0]
  $mergeMethods=@($pull.parameters.allowed_merge_methods)
  if ($mergeMethods.Count -ne 1 -or $mergeMethods[0] -cne 'squash') { throw 'Ruleset must allow squash merges only.' }
  if ($pull.parameters.required_approving_review_count -ne 0 -or -not $pull.parameters.required_review_thread_resolution -or -not $pull.parameters.dismiss_stale_reviews_on_push -or $pull.parameters.require_code_owner_review -ne $false -or $pull.parameters.require_last_push_approval -ne $false) { throw 'PR policy mismatch.' }
  $statusRule=@($actual.rules | Where-Object { $_.type -eq 'required_status_checks' })[0]
  if (-not $statusRule.parameters.strict_required_status_checks_policy) { throw 'Strict checks not enabled.' }
  $contexts=@($statusRule.parameters.required_status_checks | ForEach-Object { $_.context })
  $expectedContexts=@('CodeRabbit','Socket Security: Pull Request Alerts','Socket Security: Project Report')
  $actualContextSet=($contexts | Sort-Object -CaseSensitive) -join "`n"
  $expectedContextSet=($expectedContexts | Sort-Object -CaseSensitive) -join "`n"
  if ($contexts.Count -ne $expectedContexts.Count -or $actualContextSet -cne $expectedContextSet) { throw 'Required status check contexts do not exactly match the approved set.' }
  $null=GhJson @('api','--method','PATCH',"repos/$repo",'--input',$settingsTemp)
  $settings=GhJson @('api',"repos/$repo")
  if ($settings.allow_merge_commit -or $settings.allow_rebase_merge -or -not $settings.allow_squash_merge -or -not $settings.allow_auto_merge -or -not $settings.delete_branch_on_merge) { throw 'Repository merge settings mismatch.' }
  Write-Host "VERIFIED: ACTIVE main ruleset $rulesetId, checks, PR, threads, squash-only, no force or delete."
  Write-Host 'Require GEF Smoke CI jobs later ONLY after they exist and have passed on real PR HEAD.'
} finally {
  Remove-Item -LiteralPath $temp,$settingsTemp -Force -ErrorAction SilentlyContinue
}
