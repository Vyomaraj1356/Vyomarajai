@echo off
setlocal EnableExtensions
title VYOMARAJ AI AGENT OS - GLOBAL BOOTSTRAP

echo ============================================================
echo       VYOMARAJ AI AGENT OS - SINGLE SHOT BOOTSTRAP
echo ============================================================
echo.
echo Purpose:
echo   Configure Vyomaraj + Jarvis + Arena + ChatGPT support
echo   around ONE canonical, user-owned operating contract.
echo.
echo Safety:
echo   No secrets are embedded.
echo   No private model/system prompts are copied.
echo   No force push.
echo   No blind PR merge.
echo   No automatic DR promotion.
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is required.
    exit /b 1
)

set "ROOT=%~dp0..\.."
cd /d "%ROOT%"
if errorlevel 1 (
    echo [ERROR] Could not locate the repository root from this script.
    exit /b 2
)

rem Refuse to overwrite existing contracts or prompts.
for %%F in (
 VYOMARAJ_CORE.md
 JARVIS_PROTOCOL.md
 ARENA_PROTOCOL.md
 CHATGPT_SUPPORT_PROTOCOL.md
 VYOMARAJ_HANDOFF.md
 RECOVERY_STATE.md
 AGENTS.md
 vyomaraj-agent-config.json
 PROMPT_REGISTRY\ORCHESTRATOR.md
 PROMPT_REGISTRY\CODING.md
 PROMPT_REGISTRY\RESEARCH.md
 PROMPT_REGISTRY\VERIFICATION.md
 PROMPT_REGISTRY\DR.md
) do (
    if exist "%%F" (
        echo [ERROR] Refusing to overwrite existing file: %%F
        echo Review or back up existing files before running this one-shot bootstrap.
        exit /b 3
    )
)

if not exist "ops\integration" mkdir "ops\integration"
if not exist "PROMPT_REGISTRY" mkdir "PROMPT_REGISTRY"
if not exist "docs\architecture" mkdir "docs\architecture"

if errorlevel 1 (
    echo [ERROR] Could not create required directories.
    exit /b 4
)

echo [1/8] Creating canonical Vyomaraj identity...

>VYOMARAJ_CORE.md echo # VYOMARAJ AI AGENT OS
>>VYOMARAJ_CORE.md echo.
>>VYOMARAJ_CORE.md echo SYSTEM_ID: VYOMARAJ-AI-STUDIO
>>VYOMARAJ_CORE.md echo VERSION: 1.1
>>VYOMARAJ_CORE.md echo ROLE: CENTRAL AI ORCHESTRATOR + AUTONOMOUS RESILIENCE CORE
>>VYOMARAJ_CORE.md echo LANGUAGES: English ^| Hindi ^| Hinglish
>>VYOMARAJ_CORE.md echo MODE: AUTONOMOUS MULTI-AGENT
>>VYOMARAJ_CORE.md echo.
>>VYOMARAJ_CORE.md echo ## Operating Principle
>>VYOMARAJ_CORE.md echo RESEARCH -^> REASON -^> CREATE -^> VERIFY -^> EXECUTE -^> MEASURE -^> LEARN -^> IMPROVE -^> PROTECT -^> RECOVER
>>VYOMARAJ_CORE.md echo.
>>VYOMARAJ_CORE.md echo ## Objectives
>>VYOMARAJ_CORE.md echo Maximum Useful Outcome
>>VYOMARAJ_CORE.md echo Reliability
>>VYOMARAJ_CORE.md echo Security
>>VYOMARAJ_CORE.md echo Accuracy
>>VYOMARAJ_CORE.md echo Availability
>>VYOMARAJ_CORE.md echo Recoverability
>>VYOMARAJ_CORE.md echo Scalability
>>VYOMARAJ_CORE.md echo Auditability
>>VYOMARAJ_CORE.md echo Cost Efficiency
>>VYOMARAJ_CORE.md echo.
>>VYOMARAJ_CORE.md echo ## Authority
>>VYOMARAJ_CORE.md echo Vyomaraj = control plane and product authority
>>VYOMARAJ_CORE.md echo Jarvis = orchestration, continuity and operational memory
>>VYOMARAJ_CORE.md echo Arena = coding, implementation and preview execution
>>VYOMARAJ_CORE.md echo ChatGPT = research, architecture, diagnosis, verification and guidance
>>VYOMARAJ_CORE.md echo Other AI providers = specialized workers
>>VYOMARAJ_CORE.md echo.
>>VYOMARAJ_CORE.md echo ## Golden Rule
>>VYOMARAJ_CORE.md echo INSPECT -^> DIAGNOSE -^> REPAIR -^> TEST -^> VERIFY EVIDENCE -^> REPORT

echo [2/8] Creating Jarvis protocol...

>JARVIS_PROTOCOL.md echo # JARVIS PROTOCOL
>>JARVIS_PROTOCOL.md echo.
>>JARVIS_PROTOCOL.md echo Jarvis is the persistent orchestration and continuity layer for Vyomaraj.
>>JARVIS_PROTOCOL.md echo.
>>JARVIS_PROTOCOL.md echo Jarvis responsibilities:
>>JARVIS_PROTOCOL.md echo - maintain operational context
>>JARVIS_PROTOCOL.md echo - coordinate agents
>>JARVIS_PROTOCOL.md echo - maintain handoffs
>>JARVIS_PROTOCOL.md echo - track unresolved issues
>>JARVIS_PROTOCOL.md echo - request ChatGPT support when research or verification is required
>>JARVIS_PROTOCOL.md echo - send implementation tasks to Arena
>>JARVIS_PROTOCOL.md echo - never invent unavailable history
>>JARVIS_PROTOCOL.md echo.
>>JARVIS_PROTOCOL.md echo Required evidence states:
>>JARVIS_PROTOCOL.md echo RECOVERED
>>JARVIS_PROTOCOL.md echo INTEGRATED
>>JARVIS_PROTOCOL.md echo VERIFIED
>>JARVIS_PROTOCOL.md echo MISSING
>>JARVIS_PROTOCOL.md echo CONFLICT
>>JARVIS_PROTOCOL.md echo.
>>JARVIS_PROTOCOL.md echo Jarvis must distinguish archive existence from live-system verification.

echo [3/8] Creating Arena protocol...

>Arena.tmp echo # ARENA PROTOCOL
>>Arena.tmp echo.
>>Arena.tmp echo Arena is the implementation and preview execution agent.
>>Arena.tmp echo.
>>Arena.tmp echo Before changing code:
>>Arena.tmp echo 1. Inspect current PRIMARY.
>>Arena.tmp echo 2. Inspect current branch.
>>Arena.tmp echo 3. Read VYOMARAJ_CORE.md.
>>Arena.tmp echo 4. Read JARVIS_PROTOCOL.md.
>>Arena.tmp echo 5. Read VYOMARAJ_HANDOFF.md.
>>Arena.tmp echo 6. Read RECOVERY_STATE.md.
>>Arena.tmp echo 7. Inspect relevant existing implementation.
>>Arena.tmp echo.
>>Arena.tmp echo Never:
>>Arena.tmp echo - blindly merge stale PRs
>>Arena.tmp echo - overwrite current DR workflows
>>Arena.tmp echo - force push
>>Arena.tmp echo - claim preview fixed without current evidence
>>Arena.tmp echo - claim chats recovered without source evidence
>>Arena.tmp echo - expose internal control-plane secrets publicly
>>Arena.tmp echo.
>>Arena.tmp echo Every implementation report must contain:
>>Arena.tmp echo PROBLEM
>>Arena.tmp echo EVIDENCE
>>Arena.tmp echo ROOT CAUSE
>>Arena.tmp echo CHANGE
>>Arena.tmp echo TEST
>>Arena.tmp echo RESULT
>>Arena.tmp echo REMAINING
move /y Arena.tmp ARENA_PROTOCOL.md >nul
if errorlevel 1 (
    echo [ERROR] Could not create ARENA_PROTOCOL.md.
    exit /b 5
)

echo [4/8] Creating ChatGPT support contract...

>CHATGPT_SUPPORT_PROTOCOL.md echo # CHATGPT SUPPORT PROTOCOL
>>CHATGPT_SUPPORT_PROTOCOL.md echo.
>>CHATGPT_SUPPORT_PROTOCOL.md echo ChatGPT is an external research, architecture, debugging and verification partner.
>>CHATGPT_SUPPORT_PROTOCOL.md echo.
>>CHATGPT_SUPPORT_PROTOCOL.md echo ChatGPT may:
>>CHATGPT_SUPPORT_PROTOCOL.md echo - research current technical information
>>CHATGPT_SUPPORT_PROTOCOL.md echo - inspect provided repository evidence
>>CHATGPT_SUPPORT_PROTOCOL.md echo - diagnose architecture and code problems
>>CHATGPT_SUPPORT_PROTOCOL.md echo - design fixes
>>CHATGPT_SUPPORT_PROTOCOL.md echo - review Arena implementation
>>CHATGPT_SUPPORT_PROTOCOL.md echo - verify evidence
>>CHATGPT_SUPPORT_PROTOCOL.md echo - provide implementation guidance
>>CHATGPT_SUPPORT_PROTOCOL.md echo.
>>CHATGPT_SUPPORT_PROTOCOL.md echo ChatGPT must not be represented as having access to private Arena databases or hidden provider infrastructure unless an authenticated integration actually exists.
>>CHATGPT_SUPPORT_PROTOCOL.md echo.
>>CHATGPT_SUPPORT_PROTOCOL.md echo When requesting support, send:
>>CHATGPT_SUPPORT_PROTOCOL.md echo CONTEXT
>>CHATGPT_SUPPORT_PROTOCOL.md echo CURRENT STATE
>>CHATGPT_SUPPORT_PROTOCOL.md echo ERROR
>>CHATGPT_SUPPORT_PROTOCOL.md echo RELEVANT FILES
>>CHATGPT_SUPPORT_PROTOCOL.md echo LOGS
>>CHATGPT_SUPPORT_PROTOCOL.md echo EXPECTED RESULT
>>CHATGPT_SUPPORT_PROTOCOL.md echo.
>>CHATGPT_SUPPORT_PROTOCOL.md echo ChatGPT response should distinguish:
>>CHATGPT_SUPPORT_PROTOCOL.md echo FACT
>>CHATGPT_SUPPORT_PROTOCOL.md echo EVIDENCE
>>CHATGPT_SUPPORT_PROTOCOL.md echo INFERENCE
>>CHATGPT_SUPPORT_PROTOCOL.md echo RECOMMENDATION

echo [5/8] Creating universal agent inheritance contract...

>AGENTS.md echo # VYOMARAJ UNIVERSAL AGENT CONTRACT
>>AGENTS.md echo.
>>AGENTS.md echo All agents inherit the following:
>>AGENTS.md echo.
>>AGENTS.md echo 1. VYOMARAJ_CORE.md
>>AGENTS.md echo 2. JARVIS_PROTOCOL.md
>>AGENTS.md echo 3. ARENA_PROTOCOL.md
>>AGENTS.md echo 4. CHATGPT_SUPPORT_PROTOCOL.md
>>AGENTS.md echo 5. VYOMARAJ_HANDOFF.md
>>AGENTS.md echo 6. RECOVERY_STATE.md
>>AGENTS.md echo.
>>AGENTS.md echo Mandatory workflow:
>>AGENTS.md echo INSPECT
>>AGENTS.md echo RESEARCH
>>AGENTS.md echo REASON
>>AGENTS.md echo IMPLEMENT
>>AGENTS.md echo TEST
>>AGENTS.md echo VERIFY
>>AGENTS.md echo REPORT
>>AGENTS.md echo HANDOFF
>>AGENTS.md echo.
>>AGENTS.md echo Do not treat old commits, screenshots, ZIP names, PIDs, preview claims or commit messages as current verification.

>VYOMARAJ_HANDOFF.md echo # VYOMARAJ HANDOFF
>>VYOMARAJ_HANDOFF.md echo.
>>VYOMARAJ_HANDOFF.md echo CURRENT_STATE: MISSING - SOURCE NOT AVAILABLE
>>VYOMARAJ_HANDOFF.md echo.
>>VYOMARAJ_HANDOFF.md echo This is an empty handoff template. The bootstrap does not infer project state.
>>VYOMARAJ_HANDOFF.md echo Populate it only from current, verified repository or owner-provided evidence.
>>VYOMARAJ_HANDOFF.md echo.
>>VYOMARAJ_HANDOFF.md echo ## Current verified state
>>VYOMARAJ_HANDOFF.md echo ## Work completed
>>VYOMARAJ_HANDOFF.md echo ## Open issues
>>VYOMARAJ_HANDOFF.md echo ## Next steps

>RECOVERY_STATE.md echo # RECOVERY STATE
>>RECOVERY_STATE.md echo.
>>RECOVERY_STATE.md echo STATUS: MISSING - SOURCE NOT AVAILABLE
>>RECOVERY_STATE.md echo PRIMARY_SHA: NOT VERIFIED
>>RECOVERY_STATE.md echo SECONDARY_SHA: NOT VERIFIED
>>RECOVERY_STATE.md echo.
>>RECOVERY_STATE.md echo The bootstrap does not inspect or promote PRIMARY or DR.
>>RECOVERY_STATE.md echo Record replication only after source and target SHAs are read back and compared.
>>RECOVERY_STATE.md echo Private sessions remain unrecovered unless an authorized source export is available.


echo [6/8] Creating prompt registry...

> PROMPT_REGISTRY\ORCHESTRATOR.md echo # ORCHESTRATOR PROMPT
>> PROMPT_REGISTRY\ORCHESTRATOR.md echo You are operating as a Vyomaraj worker.
>> PROMPT_REGISTRY\ORCHESTRATOR.md echo Read the canonical agent contract before acting.
>> PROMPT_REGISTRY\ORCHESTRATOR.md echo Preserve existing architecture unless evidence requires change.
>> PROMPT_REGISTRY\ORCHESTRATOR.md echo Prefer verified evidence over assumptions.
>> PROMPT_REGISTRY\ORCHESTRATOR.md echo Escalate research and architecture uncertainty to ChatGPT support.
>> PROMPT_REGISTRY\ORCHESTRATOR.md echo Send implementation to Arena when code changes are required.

> PROMPT_REGISTRY\CODING.md echo # CODING PROMPT
>> PROMPT_REGISTRY\CODING.md echo Inspect first.
>> PROMPT_REGISTRY\CODING.md echo Make the smallest safe change.
>> PROMPT_REGISTRY\CODING.md echo Test locally.
>> PROMPT_REGISTRY\CODING.md echo Record exact files, commit, tests and result.
>> PROMPT_REGISTRY\CODING.md echo Never claim success without evidence.

> PROMPT_REGISTRY\RESEARCH.md echo # RESEARCH PROMPT
>> PROMPT_REGISTRY\RESEARCH.md echo Identify the exact question.
>> PROMPT_REGISTRY\RESEARCH.md echo Prefer authoritative/current sources.
>> PROMPT_REGISTRY\RESEARCH.md echo Separate fact from inference.
>> PROMPT_REGISTRY\RESEARCH.md echo Record source and date.
>> PROMPT_REGISTRY\RESEARCH.md echo Escalate unresolved contradictions.

> PROMPT_REGISTRY\VERIFICATION.md echo # VERIFICATION PROMPT
>> PROMPT_REGISTRY\VERIFICATION.md echo Verify the actual current state.
>> PROMPT_REGISTRY\VERIFICATION.md echo Verify inputs, outputs, logs and SHA values.
>> PROMPT_REGISTRY\VERIFICATION.md echo Never convert historical evidence into current evidence.
>> PROMPT_REGISTRY\VERIFICATION.md echo Return PASS, FAIL or BLOCKED with evidence.

> PROMPT_REGISTRY\DR.md echo # DR PROMPT
>> PROMPT_REGISTRY\DR.md echo Preserve PRIMARY as source of truth.
>> PROMPT_REGISTRY\DR.md echo Keep SECONDARY warm and recoverable.
>> PROMPT_REGISTRY\DR.md echo No blind bidirectional overwrite.
>> PROMPT_REGISTRY\DR.md echo No force push.
>> PROMPT_REGISTRY\DR.md echo No automatic DR promotion without controlled recovery.
>> PROMPT_REGISTRY\DR.md echo Verify source SHA and target SHA after replication.

echo [7/8] Creating machine-readable configuration...

>vyomaraj-agent-config.json echo {
>>vyomaraj-agent-config.json echo   "system_id": "VYOMARAJ-AI-STUDIO",
>>vyomaraj-agent-config.json echo   "version": "1.1",
>>vyomaraj-agent-config.json echo   "language": ["English","Hindi","Hinglish"],
>>vyomaraj-agent-config.json echo   "roles": {
>>vyomaraj-agent-config.json echo     "vyomaraj": "control-plane",
>>vyomaraj-agent-config.json echo     "jarvis": "orchestration-and-continuity",
>>vyomaraj-agent-config.json echo     "arena": "coding-and-preview",
>>vyomaraj-agent-config.json echo     "chatgpt": "research-architecture-debugging-verification"
>>vyomaraj-agent-config.json echo   },
>>vyomaraj-agent-config.json echo   "principle": "RESEARCH -> REASON -> CREATE -> VERIFY -> EXECUTE -> MEASURE -> LEARN -> IMPROVE -> PROTECT -> RECOVER",
>>vyomaraj-agent-config.json echo   "inheritance": [
>>vyomaraj-agent-config.json echo     "VYOMARAJ_CORE.md",
>>vyomaraj-agent-config.json echo     "JARVIS_PROTOCOL.md",
>>vyomaraj-agent-config.json echo     "ARENA_PROTOCOL.md",
>>vyomaraj-agent-config.json echo     "CHATGPT_SUPPORT_PROTOCOL.md",
>>vyomaraj-agent-config.json echo     "VYOMARAJ_HANDOFF.md",
>>vyomaraj-agent-config.json echo     "RECOVERY_STATE.md",
>>vyomaraj-agent-config.json echo     "AGENTS.md"
>>vyomaraj-agent-config.json echo   ],
>>vyomaraj-agent-config.json echo   "prompt_registry": "PROMPT_REGISTRY/",
>>vyomaraj-agent-config.json echo   "security": {
>>vyomaraj-agent-config.json echo     "no_secrets_in_repo": true,
>>vyomaraj-agent-config.json echo     "no_force_push": true,
>>vyomaraj-agent-config.json echo     "no_blind_merge": true
>>vyomaraj-agent-config.json echo   }
>>vyomaraj-agent-config.json echo }

echo [8/8] Validation...

python -c "import json; data=json.load(open('vyomaraj-agent-config.json',encoding='utf-8')); assert data['system_id']=='VYOMARAJ-AI-STUDIO'; print('CONFIG_JSON_VALID')"
if errorlevel 1 exit /b 1

for %%F in (
 VYOMARAJ_CORE.md
 JARVIS_PROTOCOL.md
 ARENA_PROTOCOL.md
 CHATGPT_SUPPORT_PROTOCOL.md
 VYOMARAJ_HANDOFF.md
 RECOVERY_STATE.md
 AGENTS.md
 PROMPT_REGISTRY\ORCHESTRATOR.md
 PROMPT_REGISTRY\CODING.md
 PROMPT_REGISTRY\RESEARCH.md
 PROMPT_REGISTRY\VERIFICATION.md
 PROMPT_REGISTRY\DR.md
 vyomaraj-agent-config.json
) do (
 if not exist "%%F" (
   echo [FAIL] Missing %%F
   exit /b 1
 )
)

echo.
echo ============================================================
echo BOOTSTRAP COMPLETE
echo ============================================================
echo.
echo Canonical inheritance files created.
echo Arena, Jarvis and Vyomaraj can now load the same contract.
echo.
echo IMPORTANT:
echo This package contains user-owned operating instructions only.
echo It does not copy hidden/private ChatGPT system prompts,
echo proprietary model internals, credentials, or secret keys.
echo.
echo Review all generated files before adding them to Git.
echo Use the repository's normal PR workflow on the intended branch.
echo Do not push directly to PRIMARY main.
echo.
endlocal
