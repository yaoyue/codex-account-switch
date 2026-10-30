import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex-account-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.active = self.root / "共享状态"
        self.accounts = self.root / "账号副本"
        self.bin = self.root / "bin"
        self.args_file = self.root / "vscode参数.json"
        self.active.mkdir()
        self.bin.mkdir()
        fake_code = self.bin / "code"
        fake_code.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['TEST_CODE_ARGS']).write_text(json.dumps(sys.argv[1:]))\n"
        )
        fake_code.chmod(0o755)
        self.env = dict(
            os.environ,
            CODEX_HOME=str(self.active),
            CODEX_ACCOUNT_ROOT=str(self.accounts),
            TEST_CODE_ARGS=str(self.args_file),
            PATH=os.pathsep.join((str(REPO), str(self.bin), os.environ["PATH"])),
        )

    def run_command(self, *args, expected=0):
        result = subprocess.run(
            [str(REPO / "codex-account"), *args],
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def save(self, label, version=1):
        fixture = json.dumps({"测试账号": label, "版本": version})
        (self.active / "auth.json").write_text(fixture)
        self.run_command("save-current", label)
        return fixture

    def snapshot(self):
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }

    def test_empty_and_missing_credentials(self):
        output = self.run_command("status").stdout
        self.assertIn("当前标记: 未设置", output)
        self.assertIn("尚未保存任何账号", output)
        self.assertFalse(self.accounts.exists())
        self.run_command("save-current", "personal", expected=1)
        self.assertFalse(self.accounts.exists())

    def test_more_than_three_accounts_and_shared_files(self):
        labels = ("personal", "work", "team-2", "project-4", "account_5", "account6")
        (self.active / "config.toml").write_text("共享配置")
        (self.active / "历史记录.txt").write_text("共享历史")
        fixtures = {label: self.save(label) for label in labels}
        # 无效目录和没有凭据的目录不应出现在账号列表中。
        (self.accounts / ".隐藏目录").mkdir()
        (self.accounts / ".隐藏目录" / "auth.json").write_text("{}")
        (self.accounts / "unused").mkdir()
        output = self.run_command("status").stdout
        for label in labels:
            self.assertIn(f"{label}: 已保存", output)
        self.assertNotIn("unused:", output)
        self.assertNotIn(".隐藏目录:", output)
        self.assertEqual(output.count(": 已保存"), len(labels))
        for label in labels:
            self.run_command("switch", label, "--new-window", "/tmp/示例 项目")
            self.assertEqual((self.active / "auth.json").read_text(), fixtures[label])
            self.assertEqual((self.accounts / "current").read_text().strip(), label)
            self.assertEqual(
                json.loads(self.args_file.read_text()), ["--new-window", "/tmp/示例 项目"]
            )
        self.assertEqual((self.active / "config.toml").read_text(), "共享配置")
        self.assertEqual((self.active / "历史记录.txt").read_text(), "共享历史")
        for label, fixture in fixtures.items():
            self.assertEqual((self.accounts / label / "auth.json").read_text(), fixture)

    def test_backup_and_permissions(self):
        old = self.save("personal")
        self.save("work")
        original_work = (self.accounts / "work" / "auth.json").read_bytes()
        current = self.save("personal", version=2)
        account_dir = self.accounts / "personal"
        backups = list((account_dir / "backups").glob("auth.*.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), old)
        self.assertEqual((account_dir / "auth.json").read_text(), current)
        self.assertEqual((self.accounts / "work" / "auth.json").read_bytes(), original_work)
        self.assertEqual(stat.S_IMODE(account_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((account_dir / "auth.json").stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(backups[0].stat().st_mode), 0o600)

    def test_invalid_labels_do_not_change_files(self):
        self.save("personal")
        # 上级目录也放模拟凭据，确保非法标签不会读取或覆盖这些文件。
        (self.root / "auth.json").write_text('{"测试": "不可修改"}')
        original = self.snapshot()
        labels = ("", "current", "CURRENT", "Current", "cUrReNt", ".", "..", "../escape", "a/b", "/tmp/escape", "-work", "_work", "a b", "a@example.test", "中文", "café", "a\nb")
        for label in labels:
            with self.subTest(label=label):
                for command in ("save-current", "switch"):
                    result = self.run_command(command, label, expected=1)
                    self.assertIn("账号标签须", result.stderr)
                    self.assertEqual(self.snapshot(), original)

    def test_missing_account_does_not_switch(self):
        self.save("personal")
        original = self.snapshot()
        self.run_command("switch", "missing", expected=1)
        self.assertEqual(self.snapshot(), original)

    def test_existing_wrappers_remain_compatible(self):
        for wrapper in sorted(REPO.glob("code-*")):
            label = wrapper.name.removeprefix("code-")
            with self.subTest(wrapper=wrapper.name):
                fixture = self.save(label)
                result = subprocess.run(
                    [str(wrapper), "--new-window", "/tmp/快捷 项目"],
                    env=self.env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((self.active / "auth.json").read_text(), fixture)
                self.assertEqual(
                    json.loads(self.args_file.read_text()), ["--new-window", "/tmp/快捷 项目"]
                )
        self.run_command("switch", label)
        self.assertEqual(json.loads(self.args_file.read_text()), ["."])


if __name__ == "__main__":
    unittest.main()
