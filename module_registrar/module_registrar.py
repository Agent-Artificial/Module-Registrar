import os
import json
import jsonpickle
import base64
from pathlib import Path


class ModuleRegistrar:
    def __init__(self, storage_path='module_registrar/modules/registry/module_registry.json'):
        self.storage_path = Path(storage_path)
        self.registry = json.loads(self.storage_path.read_text()) if os.path.exists(storage_path) else {}
        self.load_modules()
        self.ignore_list = (".venv", "data", ".", "__py", "node_modules")

    def register(self, name, module_path):
        module_path = Path(f"{module_path}/{name}_module.py")
        self.registry[name] = json.loads(jsonpickle.encode(module_path.read_text(encoding="utf-8")))
        self.save_modules()
    
    def validate_module(self, module_name: str):
        return self.registry[module_name] if module_name in self.registry else False
        
    def save_modules(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.registry, indent=4))

    def get(self, name):
        return self.registry.get(name)
            
    def add_module(self, name, module_path):
        self.registry[name] = f"{module_path}/{name}_module.py"
        self.save_modules()
        self.generate_script(name, module_path, f"{module_path}/setup_{name}.py")
        self.register(name, module_path)
        
    def update_module(self, name, module_path):
        self.registry[name] = module_path
        self.save_modules()
        
    def remove_module(self, name):
        if name in self.registry:
            del self.registry[name]
            self.save_modules()
    
    def list_modules(self):
        return list(self.registry.keys())

    def load_modules(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                serialized = f.read()
            self.registry = jsonpickle.decode(serialized)
        else:
            self.registry = {}

    def walk_and_encode(self, folder_path):
        file_data = []
        
        for root, dirs, files in os.walk(folder_path):
            if len(dirs) > 0:
                for dir in dirs:
                    if dir.startswith(self.ignore_list):
                        continue
                    self.walk_and_encode(os.path.join(root, dir))
            for file in files:
                if file.endswith(('.sh', '.py')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, folder_path)
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        encoded_content = base64.b64encode(content).decode('utf-8')
                    file_data.append((relative_path, encoded_content))
        return file_data

    def generate_script(self, name, folder_path, output_script_name):
        file_data = self.walk_and_encode(folder_path)

        with open(output_script_name, 'w', encoding='utf-8') as script:
            script.write("import os\n")
            script.write("import base64\n")
            script.write("import subprocess\n\n")
            script.write(f"folder_path = '{folder_path}'\n\n")
            script.write("file_data = [\n")
            for path, content in file_data:
                script.write(f"    ('{path}', '{content}'),\n")
            script.write("]\n\n")

            script.write("for relative_path, encoded_content in file_data:\n")
            script.write("    full_path = os.path.join(folder_path, relative_path)\n")
            script.write("    os.makedirs(os.path.dirname(full_path), exist_ok=True)\n")
            script.write("    with open(full_path, 'wb') as f:\n")
            script.write("        f.write(base64.b64decode(encoded_content))\n")
            script.write("    print(f'Created: {full_path}')\n")
            script.write(f"subprocess.run(['python', 'module_registrar/modules/{name}/install_{name}.py'], check=True)\n")

    def clean_up(self, module_name, module_path):
        if os.path.isdir(module_path):
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.startswith(f"install_{module_name}.py"):
                        continue
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(module_path)
        

def test_save_module():
    registrar = ModuleRegistrar()
    speech2text_path = "module_registrar/modules/whisper/speech2text_module.py"
    with open(speech2text_path, 'r', encoding='utf-8') as f:
        content = f.read()
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        registrar.register("speech2text", encoded_content)

    registrar.save_modules()

def cli():
    registrar = ModuleRegistrar()
    print("Module Registry: ", registrar.registry)
    print("Options: ")
    print("1. Add Module")
    print("2. Update Module")
    print("3. Remove Module")
    print("4. List Modules")
    print("5. Clean up module")
    print("5. Exit")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            name = input("Enter the name of the module: ")
            module_path = f"module_registrar/modules/{name}"
            registrar.add_module(name, module_path)
        elif choice == "2":
            name = input("Enter the name of the module: ")
            module_path = input("Enter the path of the module: ")
            registrar.update_module(name, module_path)
        elif choice == "3":
            name = input("Enter the name of the module: ")
            registrar.remove_module(name)
        elif choice == "4":
            modules = registrar.list_modules()
            print("Modules: ", modules)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    cli()
    
