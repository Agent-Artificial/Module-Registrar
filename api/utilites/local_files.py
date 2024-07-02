import json
from pathlib import Path
from loguru import logger
from typing import List, Union


def open_local_file(path: Union[Path, str]="data/querymaps") -> List[str]:
    if path:
        path = Path(path)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        else:
            logger.error(f'File does not exist: {path}')

    return []


def save_local_file(path: Union[Path, str], data: List[str]):
    if path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)


    
    
    

