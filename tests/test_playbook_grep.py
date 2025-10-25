import unittest

from playbook import PlaybookOperator


class TestPlaybookGrep(unittest.TestCase):
    def setUp(self):
        # 创建PlaybookOperator实例
        self.operator = PlaybookOperator()

    def test_grep_playbook(self):
        results = self.operator.grep("保单文件")
        self.assertGreater(len(results), 1)
        print(results)

if __name__ == '__main__':
    unittest.main()