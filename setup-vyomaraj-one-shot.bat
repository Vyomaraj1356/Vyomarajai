@echo off
setlocal EnableExtensions

title VYOMARAJ ONE-SHOT SETUP

echo.
echo ==========================================================
echo        VYOMARAJ AI AGENT OS - ONE SHOT SETUP
echo ==========================================================
echo.
echo This configures the shared:
echo   VYOMARAJ + JARVIS + ARENA + CHATGPT SUPPORT
echo   SECURITY + DR + INHERITANCE architecture.
echo.
echo No secrets are created or displayed.
echo No force-push or destructive operation is performed.
echo.

cd /d "%~dp0"

where powershell.exe >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is required.
    pause
    exit /b 10
)

if not exist ".git" (
    echo ERROR: Run this file from the ROOT of the Vyomaraj Git repository.
    echo.
    echo Current folder:
    cd
    pause
    exit /b 11
)

rem Refuse to overwrite any existing files from a prior or partial setup.
for %%F in (
 VYOMARAJ_SHARED\VYOMARAJ_CORE.md
 VYOMARAJ_SHARED\JARVIS_PROTOCOL.md
 VYOMARAJ_SHARED\ARENA_PROTOCOL.md
 VYOMARAJ_SHARED\CHATGPT_SUPPORT_PROTOCOL.md
 VYOMARAJ_SHARED\inheritance-manifest.json
 VYOMARAJ_SHARED\SECURITY\SECURITY_RULES.md
 VYOMARAJ_SHARED\DR\DR_RULES.md
) do (
    if exist "%%F" (
        echo ERROR: Refusing to overwrite existing file: %%F
        echo Review or back up existing files before running this one-shot setup.
        pause
        exit /b 12
    )
)

echo [1/8] Creating shared directories...

mkdir "VYOMARAJ_SHARED" 2>nul
mkdir "VYOMARAJ_SHARED\PROMPT_REGISTRY" 2>nul
mkdir "VYOMARAJ_SHARED\STATE" 2>nul
mkdir "VYOMARAJ_SHARED\SECURITY" 2>nul
mkdir "VYOMARAJ_SHARED\DR" 2>nul
mkdir "reports\vyomaraj" 2>nul

echo [2/8] Creating VYOMARAJ core...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; $p='VYOMARAJ_SHARED\VYOMARAJ_CORE.md'; @'
# VYOMARAJ AI AGENT OS

SYSTEM_ID: VYOMARAJ-AI-STUDIO
ROLE: CENTRAL AI ORCHESTRATOR + AUTONOMOUS RESILIENCE CORE
MODE: AUTONOMOUS MULTI-AGENT
LANGUAGES: English | Hindi | Hinglish

OPERATING LOOP:

RESEARCH
-> REASON
-> CREATE
-> VERIFY
-> EXECUTE
-> MEASURE
-> LEARN
-> IMPROVE
-> PROTECT
-> RECOVER

AUTHORITY:

VYOMARAJ = CONTROL-PLANE AUTHORITY
JARVIS = ORCHESTRATION + CONTINUITY
ARENA = CODING + IMPLEMENTATION + PREVIEW
CHATGPT = RESEARCH + ARCHITECTURE + DEBUGGING + VERIFICATION
OTHER AI PROVIDERS = SPECIALIZED WORKERS

PRIMARY:

Vyomaraj1356/Vyomarajai

DR / SECONDARY:

deepakGoyal1356/Vyomaraj-Agent-6d64e

PRIMARY is the canonical source of truth.

DR is the recoverable secondary.

ARENA inherits approved configuration from PRIMARY.

No agent may silently replace the canonical authority model.

PUBLIC BOUNDARY:

The internal Vyomaraj control plane remains private.

Public users should receive approved creations, content, views, likes, subscribers and public-facing outputs, not internal credentials, control-plane state or private operational data.
'@ | Set-Content -Encoding UTF8 -LiteralPath $p"

if errorlevel 1 exit /b 20

echo [3/8] Creating JARVIS protocol...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; $p='VYOMARAJ_SHARED\JARVIS_PROTOCOL.md'; @'
# JARVIS PROTOCOL

JARVIS is the persistent orchestration and continuity layer for Vyomaraj.

Responsibilities:

1. Maintain project continuity.
2. Read the current canonical Vyomaraj state.
3. Coordinate Arena implementation.
4. Coordinate specialist AI workers.
5. Preserve handoffs.
6. Track unresolved issues.
7. Never convert an unverified claim into a verified fact.
8. Escalate security and integrity concerns.
9. Verify implementation before declaring completion.

GOLDEN LOOP:

INSPECT
-> DIAGNOSE
-> IMPLEMENT
-> TEST
-> VERIFY
-> REPORT
-> HANDOFF

Evidence states:

FACT
EVIDENCE
INFERENCE
UNVERIFIED
RECOVERED
MISSING
VERIFIED
'@ | Set-Content -Encoding UTF8 -LiteralPath $p"

if errorlevel 1 exit /b 21

echo [4/8] Creating ARENA protocol...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; $p='VYOMARAJ_SHARED\ARENA_PROTOCOL.md'; @'
# ARENA PROTOCOL

ARENA is the implementation and preview execution environment.

ARENA must:

1. Inherit the current approved Vyomaraj configuration.
2. Read VYOMARAJ_CORE.
3. Read JARVIS_PROTOCOL.
4. Read this protocol.
5. Preserve current security and DR workflows.
6. Work on branches/PRs rather than blindly modifying production authority.
7. Test before claiming completion.
8. Produce evidence for changes.
9. Never claim chat/session recovery without an actual source.
10. Never claim Primary/DR synchronization without verified evidence.

ARENA MUST NOT:

- expose secrets
- weaken security controls
- replace DR architecture
- force-push
- blindly overwrite PRIMARY
- automatically promote DR to PRIMARY
- execute untrusted recovery archives
- fabricate missing chat history

PREVIEW RULE:

The preview must represent the current verified Vyomaraj state, not merely an old Arena screenshot or historical claim.
'@ | Set-Content -Encoding UTF8 -LiteralPath $p"

if errorlevel 1 exit /b 22

echo [5/8] Creating CHATGPT support contract...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; $p='VYOMARAJ_SHARED\CHATGPT_SUPPORT_PROTOCOL.md'; @'
# CHATGPT SUPPORT PROTOCOL

CHATGPT SUPPORT ROLE:

Research
Architecture
Technical diagnosis
Debugging
Verification
Security reasoning
Recovery reasoning
Documentation support

When requesting support, provide:

1. CURRENT STATE
2. EXPECTED STATE
3. ERROR / PROBLEM
4. RELEVANT FILE
5. RELEVANT LOG
6. COMMIT / RUN ID when available
7. EXPECTED RESULT

CHATGPT response categories:

FACT
EVIDENCE
ROOT CAUSE
RECOMMENDATION
CHANGE
TEST
VERIFICATION
REMAINING RISK

CHATGPT must not claim access to private Arena databases, private sessions, credentials or external systems unless an actual authorized connector provides that access.

Missing information must remain:

UNRECOVERED - SOURCE NOT AVAILABLE

ChatGPT private system/developer instructions, hidden reasoning and credentials are never copied into this repository.

Only the user-owned Vyomaraj operating contract and project instructions are inherited.
'@ | Set-Content -Encoding UTF8 -LiteralPath $p"

if errorlevel 1 exit /b 23

echo [6/8] Creating inheritance manifest...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; $p='VYOMARAJ_SHARED\inheritance-manifest.json'; @'
{
  "system": "VYOMARAJ-AI-STUDIO",
  "version": "1.1",
  "authority": {
    "canonical": "Vyomaraj1356/Vyomarajai",
    "dr": "deepakGoyal1356/Vyomaraj-Agent-6d64e"
  },
  "roles": {
    "vyomaraj": "control-plane-authority",
    "jarvis": "orchestration-and-continuity",
    "arena": "coding-implementation-preview",
    "chatgpt": "research-architecture-debugging-verification"
  },
  "arena_inheritance": {
    "enabled": true,
    "source": "PRIMARY",
    "automatic_force_push": false,
    "automatic_primary_overwrite": false,
    "automatic_security_override": false
  },
  "dr": {
    "primary_to_secondary": true,
    "sha_verification_required": true,
    "read_after_write_required": true,
    "automatic_force_push": false,
    "automatic_dr_to_primary": false
  },
  "security": {
    "secret_values_in_logs": false,
    "automatic_delete": false,
    "untrusted_execution": false,
    "integrity_verification_required": true
  }
}
'@ | Set-Content -Encoding UTF8 -LiteralPath $p"

if errorlevel 1 exit /b 24

echo [7/8] Creating security and DR rules...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; $p='VYOMARAJ_SHARED\SECURITY\SECURITY_RULES.md'; @'
# VYOMARAJ SECURITY RULES

DETECT
-> PRESERVE EVIDENCE
-> CONTAIN
-> VERIFY
-> RECOVER
-> RECHECK
-> RESUME

Rules:

- Never expose credentials.
- Never store secret values in reports.
- Never execute untrusted archives.
- Never blindly replicate a suspected compromise.
- Never force-push during recovery.
- Never automatically promote DR to PRIMARY.
- Hash critical files.
- Verify repository integrity.
- Treat suspicious files as indicators requiring review, not automatic proof of malware.

If compromise is suspected:

PAUSE REPLICATION
-> PRESERVE EVIDENCE
-> VERIFY PRIMARY
-> VERIFY DR
-> CONTAIN
-> RECOVER
-> VERIFY
-> RESUME
'@ | Set-Content -Encoding UTF8 -LiteralPath $p; $p='VYOMARAJ_SHARED\DR\DR_RULES.md'; @'
# VYOMARAJ DR RULES

PRIMARY:
Vyomaraj1356/Vyomarajai

SECONDARY:
deepakGoyal1356/Vyomaraj-Agent-6d64e

Normal direction:

PRIMARY -> SECONDARY

DR -> PRIMARY is controlled recovery only.

Required before synchronization claim:

1. Primary reachable.
2. Secondary reachable.
3. Authentication verified.
4. Source SHA known.
5. Target update completed.
6. Read-after-write verification completed.
7. SHA comparison completed.
8. No integrity warning.

Git replication alone is not equivalent to complete application disaster recovery.

Application data, configuration, storage, queues, jobs, knowledge, memory and audit evidence require separate recovery mechanisms.
'@ | Set-Content -Encoding UTF8 -LiteralPath $p"

if errorlevel 1 exit /b 25

echo [8/8] Validating configuration...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference='Stop'; $root='VYOMARAJ_SHARED'; $j=Get-Content -LiteralPath ($root+'\inheritance-manifest.json') -Raw | ConvertFrom-Json; if($j.system -ne 'VYOMARAJ-AI-STUDIO'){throw 'Invalid system'}; if($j.authority.dr -ne 'deepakGoyal1356/Vyomaraj-Agent-6d64e'){throw 'Invalid DR repository'}; $required=@('VYOMARAJ_CORE.md','JARVIS_PROTOCOL.md','ARENA_PROTOCOL.md','CHATGPT_SUPPORT_PROTOCOL.md','inheritance-manifest.json','SECURITY\SECURITY_RULES.md','DR\DR_RULES.md'); foreach($f in $required){$path=$root+'\'+$f; if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw ('Missing required file: '+$path)}}; Write-Host 'JSON VALID'; foreach($f in $required){Write-Host ('OK  '+($root+'\'+$f))}"

if errorlevel 1 (
    echo.
    echo ==========================================================
    echo CONFIGURATION VALIDATION FAILED
    echo ==========================================================
    pause
    exit /b 20
)

echo.
echo ==========================================================
echo        VYOMARAJ ONE-SHOT SETUP COMPLETE
echo ==========================================================
echo.
echo Created:
echo.
echo   VYOMARAJ_SHARED\VYOMARAJ_CORE.md
echo   VYOMARAJ_SHARED\JARVIS_PROTOCOL.md
echo   VYOMARAJ_SHARED\ARENA_PROTOCOL.md
echo   VYOMARAJ_SHARED\CHATGPT_SUPPORT_PROTOCOL.md
echo   VYOMARAJ_SHARED\inheritance-manifest.json
echo   VYOMARAJ_SHARED\SECURITY\SECURITY_RULES.md
echo   VYOMARAJ_SHARED\DR\DR_RULES.md
echo.
echo Architecture:
echo.
echo   PRIMARY
echo      ^|
echo      +----^> DR / SECONDARY
echo      ^|
echo      +----^> ARENA INHERITANCE
echo      ^|
echo      +----^> JARVIS
echo      ^|
echo      +----^> CHATGPT SUPPORT
echo.
echo IMPORTANT:
echo This script does NOT create or expose GitHub tokens.
echo Existing GitHub Actions secrets remain untouched.
echo.
echo Review the generated files, then commit them through your
echo normal GitHub PR workflow.
echo.
pause
exit /b 0
