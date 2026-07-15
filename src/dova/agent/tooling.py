from pathlib import Path
import importlib.util, sys


class Tools:
    def __init__(self):
        self.tools = []
        self.agent = None

    def load_all_tools(self):
        """
        Dynamically load all tools from the tools_list folder.
        This function should be called after all modules are imported.
        Uses qualified names to avoid shadowing built-in modules.
        """

        BASE_DIR = Path(__file__).resolve().parent
        tools_dir = (BASE_DIR / "tools").resolve()

        if not tools_dir.exists():
            print(f"Tools directory not found: {tools_dir}")
            return

        # Iterate through all Python files in the tools_list directory
        for tool_file in sorted(tools_dir.glob("*.py")):
            # Skip __init__.py and other special files
            if tool_file.name.startswith("_"):
                continue

            module_name = tool_file.stem
            qualified_name = f"tools_list.{module_name}"

            if hasattr(sys.modules, qualified_name):
                print(f"Module {qualified_name} already loaded, skipping.")
                continue

            try:
                spec = importlib.util.spec_from_file_location(qualified_name, tool_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[qualified_name] = module
                    spec.loader.exec_module(module)

                    setattr(module, 'agent', self.agent)
                    if hasattr(module, 'tools'):
                        for tool in module.tools:
                            self.tools.append(tool)
                    else:
                        print("no 'tools' list found in", qualified_name)

            except Exception as e:
                print("Tool error:", e)
