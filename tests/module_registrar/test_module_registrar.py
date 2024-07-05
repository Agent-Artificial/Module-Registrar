import os
import unittest
from pathlib import Path
from module_registrar.module_registrar import ModuleRegistrar


class TestModuleRegistrar(unittest.TestCase):
    def setUp(self):
        self.module_registrar = ModuleRegistrar()
        self.module_registrar.registry = {"embedding": "embedding"}
        
    def test_setup_file_paths(self):
        self.module_registrar.setup_file_paths("embedding", "module_registrar/modules", "modules")
        self.assertEqual(self.module_registrar.storage_path, Path("modules"))
        self.assertEqual(self.module_registrar.target_modules_path, Path("module_registrar/modules"))
        self.assertEqual(self.module_registrar.target_module_path, Path("module_registrar/modules/embedding"))
        self.assertEqual(self.module_registrar.target_module_file_path, Path("module_registrar/modules/embedding/embedding_module.py"))
        self.assertEqual(self.module_registrar.module_storage_path, Path("modules/embedding"))
        self.assertEqual(self.module_registrar.module_setup_path, Path("modules/embedding/setup_embedding.py"))
        self.assertEqual(self.module_registrar.registry_path, Path("modules/registry.json"))
        self.assertEqual(self.module_registrar.key_path, Path("data/private_key.pem"))
        
    def test_load_registry(self):
        self.module_registrar.load_registry()
        self.assertEqual(list(self.module_registrar.registry.keys()), ["embedding"])
     
    def test_add_module(self):   
        self.module_registrar.add_module("embedding", "module_registrar/modules/embedding")
        self.assertEqual(list(self.module_registrar.registry.keys()), ["embedding"])
        
    def test_save_registry(self):
        self.module_registrar.registry["pants"] = "pants"
        self.module_registrar.save_registry()
        self.assertEqual(list(self.module_registrar.registry.keys()), ["embedding" , "pants"])
    
    def test_remove_module(self):
        self.module_registrar.remove_module("pants")
        self.assertEqual(list(self.module_registrar.registry.keys()), ["embedding"])
        
    def test_list_modules(self):
        self.module_registrar.list_modules()
        self.assertEqual(list(self.module_registrar.registry.keys()), ["embedding"])
        
    def test_get(self):
        self.module_registrar.get("embedding")
        self.assertEqual(list(self.module_registrar.registry.keys()), ["embedding"])
        
    def test_register(self):
        self.module_registrar.register("embedding")
        
        
    def test_walk_and_encode(self):
        result = self.module_registrar.walk_and_encode("embedding", "module_registrar/modules/embedding")
        self.assertEqual(list(self.module_registrar.registry.keys()), ["embedding"])
        self.assertEqual(os.listdir("modules/embedding"), ["setup_embedding.py"])
        print(result)