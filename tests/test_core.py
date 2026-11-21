import unittest

from path_canonicalization_resolver import canonicalize


class TestCanonicalize(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(canonicalize("", case_insensitive=False), ".")

    def test_relative_simple(self):
        self.assertEqual(canonicalize("a/b/c", case_insensitive=False), "a/b/c")

    def test_collapses_separators(self):
        self.assertEqual(canonicalize("a//b///c", case_insensitive=False), "a/b/c")

    def test_removes_dot_segments(self):
        self.assertEqual(canonicalize("a/./b/./c", case_insensitive=False), "a/b/c")

    def test_resolves_dotdot(self):
        self.assertEqual(canonicalize("a/b/../c", case_insensitive=False), "a/c")

    def test_leading_dotdot_is_kept_for_relative(self):
        self.assertEqual(canonicalize("../a", case_insensitive=False), "../a")
        self.assertEqual(canonicalize("../../a", case_insensitive=False), "../../a")

    def test_dotdot_beyond_root_is_dropped_for_absolute(self):
        self.assertEqual(canonicalize("/a/../../b", case_insensitive=False), "/b")

    def test_absolute_root(self):
        self.assertEqual(canonicalize("/", case_insensitive=False), "/")

    def test_absolute_with_redundant_segments(self):
        self.assertEqual(canonicalize("/a//b/./c/../d", case_insensitive=False), "/a/b/d")

    def test_all_dotdot_relative(self):
        self.assertEqual(canonicalize("a/..", case_insensitive=False), ".")

    def test_all_dotdot_absolute(self):
        self.assertEqual(canonicalize("/a/..", case_insensitive=False), "/")

    def test_case_insensitive_lowercases_ascii(self):
        self.assertEqual(canonicalize("A/B/C", case_insensitive=True), "a/b/c")

    def test_case_insensitive_preserves_non_ascii(self):
        self.assertEqual(canonicalize("Ä/Ö", case_insensitive=True), "Ä/Ö")

    def test_case_sensitive_preserves_case(self):
        self.assertEqual(canonicalize("A/B/C", case_insensitive=False), "A/B/C")

    def test_nt_flavour_backslashes(self):
        self.assertEqual(canonicalize("a\\b\\c", flavour="nt", case_insensitive=False), "a\\b\\c")

    def test_nt_flavour_drive(self):
        self.assertEqual(canonicalize("C:\\a\\..\\b", flavour="nt", case_insensitive=False), "C:\\b")

    def test_nt_flavour_relative_with_dotdot(self):
        self.assertEqual(canonicalize("a\\..\\b", flavour="nt", case_insensitive=False), "b")

    def test_nt_flavour_case_insensitive(self):
        self.assertEqual(canonicalize("C:\\A\\B", flavour="nt", case_insensitive=True), "c:\\a\\b")

    def test_posix_flavour_explicit(self):
        self.assertEqual(canonicalize("a/b", flavour="posix", case_insensitive=False), "a/b")

    def test_invalid_flavour(self):
        with self.assertRaises(ValueError):
            canonicalize("a", flavour="windows")

    def test_non_string_input(self):
        with self.assertRaises(TypeError):
            canonicalize(123)


if __name__ == "__main__":
    unittest.main()
