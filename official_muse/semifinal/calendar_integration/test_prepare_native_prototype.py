"""Directory-level generator checks; no Cargo, GUI or shared-tree writes."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('prepare', Path(__file__).with_name('prepare_native_prototype.py'))
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class GeneratorTests(unittest.TestCase):
    def test_real_module_files_include_history(self):
        root = prepare.HERE / 'native-prototype'
        self.assertEqual([p.relative_to(root).as_posix() for p in prepare.module_files(root)],
                         ['Cargo.toml', 'src/history.rs', 'src/lib.rs'])

    def test_nested_modules_and_missing_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'src/nested').mkdir(parents=True)
            (root / 'Cargo.toml').write_text('')
            with self.assertRaises(ValueError):
                prepare.module_files(root)
            (root / 'src/lib.rs').write_text('mod nested;')
            (root / 'src/nested/mod.rs').write_text('')
            self.assertIn(root / 'src/nested/mod.rs', prepare.module_files(root))

    def test_existing_output_refused_without_touching_receipt(self):
        with tempfile.TemporaryDirectory(dir=prepare.HERE) as temp:
            root = Path(temp)
            receipt = root / 'NATIVE_PROTOTYPE_RESULT.json'
            receipt.write_bytes(b'frozen')
            with self.assertRaises(FileExistsError):
                prepare.create_output(root)
            self.assertEqual(receipt.read_bytes(), b'frozen')
            with self.assertRaises(ValueError):
                prepare.create_output(root / 'nested')
            new = root.with_name(root.name + '-new')
            try:
                self.assertEqual(prepare.create_output(new), new)
            finally:
                if new.exists():
                    new.rmdir()


if __name__ == '__main__':
    unittest.main()
