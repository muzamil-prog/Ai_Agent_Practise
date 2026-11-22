import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import calculator, execute_tool, get_current_time, list_files, read_text_file


class CalculatorTests(unittest.TestCase):
    def test_basic_arithmetic(self):
        self.assertEqual(calculator("(12 + 8) * 3"), "60")
        self.assertEqual(calculator("2 ** 10"), "1024")

    def test_rejects_unsafe_expressions(self):
        with self.assertRaises(ValueError):
            calculator("__import__('os').system('echo hi')")
        with self.assertRaises(ValueError):
            calculator("2 ** 100000")


class FileToolTests(unittest.TestCase):
    def test_read_repo_file(self):
        self.assertIn("Ai_Agent_Practise", read_text_file("README.md"))

    def test_blocks_path_traversal(self):
        with self.assertRaises(ValueError):
            read_text_file("../outside.txt")

    def test_blocks_env_file(self):
        with self.assertRaises(ValueError):
            read_text_file("projects/01-agent/.env")

    def test_lists_directory(self):
        self.assertIn("README.md", list_files("."))


class ExecuteToolTests(unittest.TestCase):
    def test_unknown_tool(self):
        self.assertIn("unknown tool", execute_tool("nope", "{}"))

    def test_invalid_json(self):
        self.assertIn("Error", execute_tool("calculator", "{bad json"))

    def test_timezone(self):
        self.assertIn("UTC", get_current_time("UTC"))
        self.assertIn("Error", execute_tool("get_current_time", '{"timezone": "Mars/Base"}'))


if __name__ == "__main__":
    unittest.main()
