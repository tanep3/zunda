#!/usr/bin/env python3
"""Input-to-VOICEVOX regression tests; no server or audio playback required."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import wave

SCRIPT = Path(__file__).resolve().parents[1] / "src" / "zunda"
FAKE_CURL = """#!/usr/bin/env python3
import json, os, sys, wave
a = sys.argv[1:]
if any('/audio_query' in x for x in a):
    text = next(x[5:] for x in a if x.startswith('text='))
    with open(os.environ['ZUNDA_TEST_LOG'], 'a', encoding='utf-8') as f:
        f.write(json.dumps(text, ensure_ascii=False) + '\\n')
    print('{}')
elif any('/synthesis' in x for x in a):
    target = a[a.index('-o') + 1]
    with wave.open(target, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(24000)
        f.writeframes(bytes(4800))
else:
    sys.exit(2)
"""

class Inputs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fake = self.root / "bin"
        self.fake.mkdir()
        curl = self.fake / "curl"
        curl.write_text(FAKE_CURL)
        curl.chmod(0o755)
        self.log = self.root / "requests.jsonl"
        self.output = self.root / "out.wav"
        self.env = os.environ.copy()
        self.env["PATH"] = str(self.fake) + os.pathsep + self.env["PATH"]
        self.env["ZUNDA_TEST_LOG"] = str(self.log)
        self.env["LC_ALL"] = "C.UTF-8"

    def run_zunda(self, *args, data=b"", success=True):
        command = ["bash", str(SCRIPT), "-m", "1", "--sentence-interval", "0.01",
                   "--sampling-rate", "24000", "-o", str(self.output), *args]
        result = subprocess.run(command, input=data, capture_output=True, env=self.env, timeout=20)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            with wave.open(str(self.output), "rb") as wav:
                self.assertEqual(wav.getframerate(), 24000)
                self.assertGreater(wav.getnframes(), 0)
            self.assertNotIn("iconv:", result.stderr.decode(errors="replace"))
        else:
            self.assertNotEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertFalse(self.output.exists())
        return result

    def requests(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def test_utf8_file_and_empty_stdin(self):
        f = self.root / "日本語.txt"
        f.write_text('こんにちは「世界」\n', encoding="utf-8")
        self.run_zunda("-i", str(f))
        self.assertEqual(self.requests(), ['こんにちは「世界」'])

    def test_japanese_arguments_newlines_quotes_and_backslash(self):
        self.run_zunda('猫の「引用」\\path\n次の行', '二つ目')
        self.assertEqual(self.requests(), ['猫の「引用」\\path', '次の行', '二つ目'])

    def test_stdin_crlf(self):
        self.run_zunda(data='最初\r\n次の行\r\n'.encode())
        self.assertEqual(self.requests(), ['最初', '次の行'])

    def test_carriage_return_removed_after_conversion(self):
        self.run_zunda(data='文字\r列\n'.encode())
        self.assertEqual(self.requests(), ['文字列'])

    def test_utf16_input_converted_before_cr_removal(self):
        self.run_zunda('--input-encoding', 'UTF-16', data='日本\r語\n'.encode('utf-16'))
        self.assertEqual(self.requests(), ['日本語'])

    def test_combined_source_order(self):
        f = self.root / "input.txt"
        f.write_text('ファイル', encoding='utf-8')
        self.run_zunda('引数一', '引数二', '-i', str(f), data='標準入力'.encode())
        self.assertEqual(self.requests(), ['標準入力', '引数一', '引数二', 'ファイル'])

    def test_explicit_shift_jis_file(self):
        f = self.root / "shiftjis.txt"
        f.write_bytes('文字コード'.encode('shift_jis'))
        self.run_zunda('--input-encoding', 'SHIFT-JIS', '-i', str(f))
        self.assertEqual(self.requests(), ['文字コード'])

    def test_explicit_euc_jp_stdin(self):
        self.run_zunda('--input-encoding', 'EUC-JP', data='日本語入力'.encode('euc_jp'))
        self.assertEqual(self.requests(), ['日本語入力'])

    def test_invalid_utf8_fails_without_requests(self):
        self.run_zunda(data=b'\xff\xfe', success=False)
        self.assertEqual(self.requests(), [])

    def test_shift_jis_without_encoding_fails(self):
        f = self.root / "shiftjis.txt"
        f.write_bytes('日本語'.encode('shift_jis'))
        self.run_zunda('-i', str(f), success=False)
        self.assertEqual(self.requests(), [])

    def test_unknown_encoding_fails(self):
        self.run_zunda('--input-encoding', 'NO-SUCH-ENCODING', data='日本語'.encode(), success=False)
        self.assertEqual(self.requests(), [])

    def test_empty_input_fails_without_requests(self):
        self.run_zunda(success=False)
        self.assertEqual(self.requests(), [])

    def test_whitespace_input_fails_without_requests(self):
        self.run_zunda(data=b' \n\r\n', success=False)
        self.assertEqual(self.requests(), [])

if __name__ == "__main__":
    unittest.main()
