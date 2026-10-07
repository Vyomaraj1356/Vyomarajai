import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESS_CONTROL = ROOT / "ops/vyomaraj/process-control.sh"
FINAL_GATE = ROOT / "ops/vyomaraj/final-readiness-gate.sh"


class ReadOnlyControlGateTests(unittest.TestCase):
    def run_script(self, path, *args):
        return subprocess.run([str(path), *args], cwd=ROOT, capture_output=True, text=True, check=False)

    def test_process_status_is_read_only(self):
        result = self.run_script(PROCESS_CONTROL, "status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"scope": "read-only repository inspection', result.stdout)
        self.assertIn('"production_status": "NOT_VERIFIED"', result.stdout)

    def test_restart_and_failover_are_blocked_without_touching_services(self):
        for command in ("start", "stop", "restart", "failover", "failback"):
            with self.subTest(command=command):
                result = self.run_script(PROCESS_CONTROL, command)
                self.assertEqual(result.returncode, 4)
                self.assertIn("BLOCKED", result.stderr)
                self.assertIn("No legacy gateway/studio writer service was contacted", result.stderr)

    def test_final_gate_reports_static_only_and_never_claims_production(self):
        result = self.run_script(FINAL_GATE)
        self.assertEqual(result.returncode, 4)
        self.assertIn("STATIC REPOSITORY CHECK: PASS", result.stdout)
        self.assertIn("RUNTIME / PRODUCTION READINESS: BLOCKED", result.stdout)
        self.assertIn("No deployment", result.stdout)

    def test_gates_have_no_production_override(self):
        for path in (PROCESS_CONTROL, FINAL_GATE):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("systemctl", text)
            self.assertNotIn("git push", text)
            self.assertNotIn("gh release", text)
            self.assertIn("read-only", text.lower())


if __name__ == "__main__":
    unittest.main()
