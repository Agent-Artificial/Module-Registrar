import os
import jsonpickle
import base64


class ModuleRegistrar:
    def __init__(self, storage_path='eden_bittensor_subnet/modules/registry/module_registry.json'):
        self.modules = {}
        self.storage_path = storage_path
        self.load_modules()

    def register(self, name, module_class):
        self.modules[name] = module_class
        self.save_modules()

    def get(self, name):
        return self.modules.get(name)

    def save_modules(self):
        serialized = jsonpickle.encode(self.modules)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            f.write(serialized)

    def load_modules(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                serialized = f.read()
            self.modules = jsonpickle.decode(serialized)
        else:
            self.modules = {}

    def walk_and_encode(self, folder_path):
        file_data = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.sh', '.py')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, folder_path)
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        encoded_content = base64.b64encode(content).decode('utf-8')
                    file_data.append((relative_path, encoded_content))
        return file_data

    def generate_script(self, folder_path, output_script_name):
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
            script.write("subprocess.run(['python', 'eden_bittensor_subnet/modules/whisper/install_whisper.py'], check=True)\n")


if __name__ == "__main__":
    registrar = ModuleRegistrar("eden_bittensor_subnet/modules/registry/module_registry.json")
    folder_to_walk = "eden_bittensor_subnet/modules/whisper"
    output_script = "eden_bittensor_subnet/modules/whisper/setup_whisper.py"
    
    registrar.generate_script(folder_to_walk, output_script)
    print(f"Script '{output_script}' has been generated.")