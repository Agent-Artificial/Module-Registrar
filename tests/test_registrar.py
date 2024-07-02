import pytest
import os
from module_registrar.module_registrar import ModuleRegistrar


@pytest.fixture(scope="class", params=["module_registrar/modules/registry/module_registry.json"])
def registrar(request):
    return ModuleRegistrar(request.param)


@pytest.fixture(scope="function", params=["module_registrar/modules/whisper"])
def folder_to_walk(request):
    return request.param

  
@pytest.fixture(scope="function", params=["module_registrar/modules/whisper/setup_whisper.py"])
def output_script(request):
    return request.param


def test_generate_script(registrar, folder_to_walk, output_script):
    registrar.generate_script(folder_path=folder_to_walk, output_script_name=output_script)
    
    assert os.path.exists(output_script)
    with open(output_script, "r", encoding="utf-8") as f:
        assert "folder_path = 'module_registrar/modules/whisper'" in f.read()

