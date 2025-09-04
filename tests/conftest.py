# Redirect any "src.trustforge[.submodule]" import to "trustforge[.submodule]"
# Works for all depths (e.g., src.trustforge.common.md).
import importlib
import importlib.abc
import importlib.util
import sys
import types

# Ensure the real package is importable first
import trustforge  # noqa: F401


class _SrcAliasImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    PREFIX = "src.trustforge"

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "src":
            # Provide a minimal dummy `src` package so namespace resolution works.
            return importlib.util.spec_from_loader("src", loader=self, is_package=True)

        if fullname.startswith(self.PREFIX):
            target_name = "trustforge" + fullname[len(self.PREFIX) :]  # replace prefix only
            target_spec = importlib.util.find_spec(target_name)
            if target_spec is None:
                return None  # let normal import machinery raise the error

            spec = importlib.util.spec_from_loader(
                fullname, loader=self, is_package=bool(target_spec.submodule_search_locations)
            )
            # keep a pointer to the real target for exec_module
            spec._alias_target = target_name  # type: ignore[attr-defined]
            return spec
        return None

    def create_module(self, spec):
        if spec.name == "src":
            mod = types.ModuleType("src")
            mod.__path__ = []  # mark as package
            return mod
        return None  # use default module creation

    def exec_module(self, module):
        if module.__name__ == "src":
            return  # nothing else to do

        target_name = getattr(module.__spec__, "_alias_target", None)  # type: ignore[attr-defined]
        if not target_name:
            return

        # Import the real module and alias it under the "src.*" name
        real_mod = importlib.import_module(target_name)
        sys.modules[module.__name__] = real_mod


# Install the alias importer at the front of sys.meta_path
# so it handles src.trustforge* before the default finders.
for finder in sys.meta_path:
    if isinstance(finder, _SrcAliasImporter):
        break
else:
    sys.meta_path.insert(0, _SrcAliasImporter())
