import pytest
import os
from eden_subnet.registrar import ModuleRegistrar


@pytest.fixture(scope="class", params=["eden_bittensor_subnet/modules/registry/module_registry.json"])
def registrar(request):
    return ModuleRegistrar(request.param)


@pytest.fixture(scope="function", params=["eden_bittensor_subnet/modules/whisper"])
def folder_to_walk(request):
    return request.param

  
@pytest.fixture(scope="function", params=["eden_bittensor_subnet/modules/whisper/setup_whisper.py"])
def output_script(request):
    return request.param


def test_generate_script(registrar, folder_to_walk, output_script):
    registrar.generate_script(folder_path=folder_to_walk, output_script_name=output_script)
    
    assert os.path.exists(output_script)
    with open(output_script, "r", encoding="utf-8") as f:
        assert "folder_path = 'eden_bittensor_subnet/modules/whisper'" in f.read()

