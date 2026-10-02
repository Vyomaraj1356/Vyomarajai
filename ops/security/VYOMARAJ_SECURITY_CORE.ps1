#requires -Version 5.1
[CmdletBinding()]
param([ValidateSet("Audit","Baseline","Incident","Verify")][string]$Mode="Audit",[string]$Root=(Get-Location).Path)
$ErrorActionPreference="Stop"; $Root=(Resolve-Path $Root).Path
$OutDir=Join-Path $Root "reports/security"; $EvidenceDir=Join-Path $Root "evidence/security"; $BaselineFile=Join-Path $Root "baseline/trusted-hashes.json"
New-Item -ItemType Directory -Force -Path $OutDir,$EvidenceDir,(Split-Path $BaselineFile) | Out-Null
function Sha256([string]$p){try{(Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLowerInvariant()}catch{$null}}
function Add-Finding($l,[string]$s,[string]$c,[string]$m,[string]$p=""){$l.Add([pscustomobject]@{severity=$s;code=$c;message=$m;path=$p})|Out-Null}
$findings=[System.Collections.Generic.List[object]]::new()
$excluded='\\.git\\|\\node_modules\\|\\reports\\security\\|\\evidence\\security\\|\\baseline\\trusted-hashes.json$'
try{$files=Get-ChildItem -LiteralPath $Root -File -Recurse -Force|?{$_.FullName -notmatch $excluded}}catch{Add-Finding $findings "HIGH" "SCAN_ERROR" $_.Exception.Message}
$current=@{}; foreach($f in $files){$h=Sha256 $f.FullName;if($h){$current[$f.FullName.Substring($Root.Length).TrimStart('\','/') ]=$h}}
if($Mode -eq "Baseline"){$current|ConvertTo-Json -Depth 3|Set-Content $BaselineFile -Encoding UTF8}
elseif(Test-Path $BaselineFile){
 try{$trusted=Get-Content $BaselineFile -Raw|ConvertFrom-Json
  foreach($p in $trusted.PSObject.Properties.Name){if(-not $current.ContainsKey($p)){Add-Finding $findings "HIGH" "FILE_DELETED" "Trusted file is missing." $p}elseif($current[$p] -ne $trusted.$p){Add-Finding $findings "HIGH" "FILE_CHANGED" "Trusted file hash changed." $p}}
  foreach($p in $current.Keys){if(-not $trusted.PSObject.Properties.Name.Contains($p)){Add-Finding $findings "MEDIUM" "FILE_NEW" "File is not present in the trusted baseline." $p}}
 }catch{Add-Finding $findings "HIGH" "BASELINE_ERROR" "Trusted baseline could not be read." $BaselineFile}
}else{Add-Finding $findings "MEDIUM" "NO_BASELINE" "No trusted baseline exists. Run Baseline only after verifying the repository." $BaselineFile}

$ext=@(".ps1",".psm1",".vbs",".vbe",".js",".jse",".hta",".cmd",".bat")
foreach($f in $files){
 if($ext -contains $f.Extension.ToLowerInvariant()){
  if($f.FullName -match '(?i)\\AppData\\(Roaming|Local)\\Microsoft\\Windows\\(Start Menu\\Programs\\Startup|Start Menu\\Programs)|\\Windows\\Temp\\|\\Users\\Public\\'){Add-Finding $findings "MEDIUM" "SCRIPT_LOCATION" "Script found in a commonly abused location." $f.FullName}
  try{$t=Get-Content $f.FullName -Raw -ErrorAction Stop;if($t -match '(?i)(FromBase64String|EncodedCommand|IEX\s*\(|Invoke-Expression|DownloadString\(|Start-BitsTransfer|rundll32|regsvr32|mshta|certutil\s+-decode|\bWebClient\b)'){Add-Finding $findings "HIGH" "SCRIPT_INDICATOR" "Potentially dangerous execution/download pattern detected; manual review required." $f.FullName}}catch{}
 }
}
try{Get-ScheduledTask|?{$_.TaskPath -notlike "\Microsoft\*"}|%{$a=$_.Actions|Out-String;if($a -match '(?i)(AppData|Temp|powershell|wscript|cscript|mshta|rundll32)'){Add-Finding $findings "HIGH" "SCHEDULED_TASK_INDICATOR" "Non-Microsoft scheduled task has a suspicious action pattern." $_.TaskName}}}catch{Add-Finding $findings "INFO" "TASK_SCAN_UNAVAILABLE" "Scheduled-task inspection was unavailable."}
try{$mp=Get-MpComputerStatus -ErrorAction Stop;if(-not $mp.RealTimeProtectionEnabled){Add-Finding $findings "HIGH" "DEFENDER_RTP_OFF" "Microsoft Defender real-time protection is disabled."};if(-not $mp.AntivirusEnabled){Add-Finding $findings "HIGH" "DEFENDER_DISABLED" "Microsoft Defender Antivirus is disabled."}}catch{Add-Finding $findings "INFO" "DEFENDER_UNAVAILABLE" "Microsoft Defender status was unavailable."}

$secretPatterns=@('(?i)github_pat_[A-Za-z0-9_\-]{20,}','(?i)gh[pousr]_[A-Za-z0-9_]{20,}','(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["''][^"'']{8,}["'']')
foreach($f in ($files|?{$_.Length -lt 2MB -and $_.Extension -in ".md",".txt",".json",".yml",".yaml",".js",".ts",".py",".ps1",".bat",".cmd",".env"})){try{$t=Get-Content $f.FullName -Raw -ErrorAction Stop;foreach($rx in $secretPatterns){if($t -match $rx){Add-Finding $findings "CRITICAL" "SECRET_PATTERN" "Possible credential/secret pattern found. Value intentionally not recorded." $f.FullName;break}}}catch{}}

$gitInfo=[ordered]@{};try{$gitInfo.commit=git -C $Root rev-parse HEAD 2>$null;$gitInfo.branch=git -C $Root branch --show-current 2>$null;$gitInfo.status=git -C $Root status --porcelain 2>$null}catch{$gitInfo.error="git inspection unavailable"}
$remote=[ordered]@{};$pr=$env:VYOMARAJ_PRIMARY_REPO;$dr=$env:VYOMARAJ_DR_REPO;$tok=$env:VYOMARAJ_PAT
if($pr -and $dr -and $tok){$headers=@{Authorization="Bearer $tok";Accept="application/vnd.github+json";"X-GitHub-Api-Version"="2022-11-28"};foreach($x in @(@{n="primary";r=$pr},@{n="dr";r=$dr})){try{$u="https://api.github.com/repos/$($x.r)/git/ref/heads/main";$z=Invoke-RestMethod -Uri $u -Headers $headers -Method Get;$remote[$x.n]=$z.object.sha}catch{$remote[$x.n]="UNAVAILABLE";Add-Finding $findings "HIGH" "REMOTE_VERIFY_FAILED" "GitHub API verification failed for the configured repository." $x.r}};if($remote.primary -and $remote.dr -and $remote.primary -ne "UNAVAILABLE" -and $remote.dr -ne "UNAVAILABLE" -and $remote.primary -ne $remote.dr){Add-Finding $findings "HIGH" "DR_SHA_MISMATCH" "Primary and DR main branches have different SHAs. Automatic promotion is blocked."}}else{Add-Finding $findings "INFO" "REMOTE_VERIFY_SKIPPED" "Authenticated remote verification skipped; configure the three environment variables to enable it."}
$id="VYOMARAJ-"+(Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$report=[ordered]@{incident_id=$id;mode=$Mode;timestamp_utc=(Get-Date).ToUniversalTime().ToString("o");host=$env:COMPUTERNAME;git=$gitInfo;remote=$remote;findings=$findings;policy=@{automatic_delete=$false;automatic_force_push=$false;automatic_dr_promotion=$false;replicate_when_integrity_unknown=$false;secret_values_recorded=$false}}
$reportPath=Join-Path $OutDir "latest-security-report.json";$report|ConvertTo-Json -Depth 8|Set-Content $reportPath -Encoding UTF8;$report|ConvertTo-Json -Depth 8|Set-Content (Join-Path $EvidenceDir "$id.json") -Encoding UTF8
Write-Host "Vyomaraj Security Guard complete: $Mode";Write-Host "Report: $reportPath";Write-Host "Findings: $($findings.Count)"
if(($findings|?{$_.severity -eq "CRITICAL"}).Count -gt 0){exit 2};if(($findings|?{$_.severity -eq "HIGH"}).Count -gt 0){exit 1};exit 0