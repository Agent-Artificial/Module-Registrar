import random
import json
import time
import os
import requests
import asyncio
from importlib import import_module
import numpy as np
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from communex.compat.key import Keypair, classic_load_key
from communex.client import CommuneClient
from communex._common import get_node_url

from fastapi.requests import Request
from scipy.spatial.distance import cosine
from module_registrar.modules.embedding.embedding_module import TokenUsage
from typing import Dict, List, Union, Optional, Tuple, Any


from dotenv import load_dotenv

from validator.data_models import (
    Message,
    ValidatorSettings,
    MinerRequest
)

load_dotenv()

comx = CommuneClient(get_node_url())

logger.level("INFO")


class Validator:
    module_name: str
    module_endpoint_url: str
    module_path: Path
    module_paths: Dict[str, Path]
    module_endpoints: Dict[str, str]
    modules = Dict[str]
    settings: ValidatorSettings
    key_name: str
    host: str
    port: int
    
    
    def __init__(
        self,
        settings: ValidatorSettings,
    ) -> None:
        self.settings =  ValidatorSettings().model_dump()
        self.module_name = settings.module_name
        self.module_endpoint_url = settings.module_endpoint_url
        self.module_path = settings.module_path
        self.module_paths = settings.module_paths
        self.module_endpoints = settings.module_endpoints
        self.modules = settings.modules
        self.key_name = settings.key_name
        self.host = settings.host
        self.port = settings.port
        

    def init_module(self, module_name: str):
        module_dir = Path(f"validator/modules/{module_name}/")
        if not module_dir.exists():
            module_dir.mkdir(parents=True, exist_ok=True)
        init_file = module_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()
        self.module_paths[module_name] = module_dir
        self.load_module(module_name)
        self.set_endpoint_url([module_name])
        self.update_modules([module_name])
        self.install_modules([module_name])
        
        
    def load_module(self, module_name: str):
        module_name = module_name.title()
        if module_name in self.module_paths:
            self.modules[module_name] = import_module(self.module_endpoints, f"{module_name}Module")
        else:
            raise ValueError(f"Module {module_name} not found in registrar")
        
    def install_modules(self, module_names: List[str]):
        for module_name in module_names:
            response = requests.get(self.module_endpoints[module_name])
            if response.status_code == 200:
                file_data = json.loads(response.text)
                file_path = Path(f"validator/module/{module_name}/{module_name}.py")
            
            
    def execute_module(self, mining_request: MinerRequest):
        module = self.modules[mining_request.inference_type]
        module.process(mining_request.request)
        
    def set_endpoint_url(self, module_names: list[str]):
        self.module_endpoints = {
            module_names: f"{self.host}:{self.port}/{module_name}" for module_name in module_names
        }
        
        
    def update_modules(self, module_names: List[str]):
        if len(module_names) > 0:
            for module_name in module_names:
                result = requests.get()
        
        
        
    def get_uid(self):
        """
        Retrieves the unique identifier associated with the validator.

        Parameters:
            None

        Returns:
            The unique identifier (uid) of the validator.

        Raises:
            ValueError: If the unique identifier (uid) is not found.
        """
        key_map = comx.query_map_key(netuid=10)
        keypair = classic_load_key(self.key_name)
        ss58_address = keypair.ss58_address
        ss58 = ""
        for uid, ss58 in key_map.items():
            if ss58 == ss58_address:
                return uid
        raise ValueError(
            f"\nUID not found, {ss58} please check your validator is registered with\n comx module info {self.key_name}"
        )

    def load_local_key(self):
        """
        Loads the local key from the specified keypath and returns a Keypair object.

        Parameters:
            self: The Validator object.

        Returns:
            Keypair: A Keypair object with the private key and SS58 address.
        """
        keypath = (
            Path(f"$HOME/.commune/key/{self.key_name}.json").expanduser().resolve()
        )
        with open(keypath, "r", encoding="utf-8") as f:
            key = json.loads(f.read())["data"]
            private_key = json.loads(key)["private_key"]
            ss58address = json.loads(key)["ss58_address"]
            return Keypair(private_key=private_key, ss58_address=ss58address)
        
    async def make_request(self, message: Message, input_url: str = ""):
        """
        Makes a request using the loaded module instead of direct API call.
        """
        logger.info("\nMaking request")
        
        try:
            result = await self.module.process(message.content, input_url)
        except Exception as e:
            logger.debug(f"\nError making request:\n{e}")
            result = []

        return result
    
    async def get_sample_result(self):
        logger.info("\nGetting sample result")
        return await self.make_request(Message(content="sample", role="user"))

    async def validate_loop(self):
        """
        Executes a loop to validate weights and scoring based on sample results and similarities.
        """
        selfuid = self.get_uid()

        address_dict = self.parse_addresses()
        weights_dict = self.parse_weights()
        weights_dict = self.check_weights(selfuid, weights_dict, address_dict)

        keys_dict = self.parse_keys()

        sample_result = await self.get_sample_result()
        prompt_message = Message(content=str(sample_result), role="user")
        encoding = tokenizer.embedding_function.encode(str(sample_result))

        similiarity_dict = await self.get_similairities(
            selfuid, encoding, prompt_message, address_dict
        )
        score_dict = self.score_modules(
            weights_dict, address_dict, keys_dict, similiarity_dict
        )
        logger.debug(score_dict)
        logger.info("\nLoading key")
        uids = []
        weights = []
        
        for uid, weight in score_dict.items():
            if uid == selfuid:
                continue
            uids.append(uid)
            weights.append(weight)
        logger.debug(f"\nuids: {uids}\nweights: {weights}")
        comx.vote(key=Keypair(self.key_name), netuid=10, weights=weights, uids=uids)
        logger.warning("Voted")
        time.sleep(60)

    def cosine_similarity(self, embedding1, embedding2):
        """
        Calculates the cosine similarity between two embeddings.

        Parameters:
            embedding1: The first embedding.
            embedding2: The second embedding.

        Returns:
            The normalized similarity value multiplied by 99.
        """
        logger.info("\nCalculating cosine similarity")
        
        # Example vectors
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Normalizing vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)

        # Calculating cosine distance
        cosine_distance = 1 -cosine(vec1_norm, vec2_norm) * 99 + 99
        if cosine_distance < 0:
            cosine_distance = 1
        logger.debug(f"\ncosine distance: {cosine_distance}")
        return round(cosine_distance - 30)
    
    def validate_input(self, embedding1, embedding2):
        """
        A function to validate input embeddings by evaluating sample similarity.

        Parameters:
            embedding1: The first embedding.
            embedding2: The second embedding.

        Returns:
            The result of the validation after evaluating the similarity.
        """
        result = None
        
        logger.info("\nEvaluating sample similarity")
        if not embedding2 and len(embedding1) != 0:
            zero_score = [0.00000001 for _ in range(len(embedding1))]
            embedding2=zero_score
        
        try:
            response = self.cosine_similarity(
                embedding1=embedding1, embedding2=embedding2
            )
            result = round(response, 2)
        except Exception as e:
            logger.error(f"\ncould not connect to miner, adjusting score.\n{e}")
            result = 1
        return result
    
    async def get_similairities(self, selfuid, encoding, prompt_message, addresses):
        """
        Retrieves similarities from different addresses by making requests and validating the responses.

        Parameters:
            selfuid: The unique identifier of the calling entity.
            encoding: The encoding type for the validation.
            prompt_message: The message used for generating the response.
            addresses: A dictionary containing UIDs and corresponding addresses.

        Returns:
            A dictionary containing the responses from different addresses after validation.
        """
        miner_responses = {}
        for uid, address in addresses.items():
            logger.info(f"\nGetting similairities - {uid}")
            if uid == selfuid:
                continue
            url = f"http://{address}/generate"
            if f"http://{self.host}:{self.port}/generate" == url:
                continue
            try:
                response = await self.make_request(
                    message=prompt_message, input_url=url
                )

                miner_responses[uid] = self.validate_input(encoding, response)
            except Exception as e:
                logger.debug(f"\nError getting similairities: {e}\n{e.args}\n")
            time.sleep(10)
        return miner_responses

    def run_voteloop(self):
        while True:
            asyncio.run(self.validate_loop())

    def parse_addresses(self):
        """
        Parses addresses and returns the result from comx.query_map_address with netuid 10.
        """
        logger.info("\nParsing addresses")
        return comx.query_map_address(netuid=10)

    def parse_weights(self):
        """
        Parses existing weights and creates a dictionary mapping UID to weight.

        Parameters:
            None

        Returns:
            dict: A dictionary mapping UID to weight based on the existing weights.
        """
        logger.info("\nParsing existing weights")
        # sourcery skip: dict-comprehension, identity-comprehension, inline-immediately-returned-variable
        weights = comx.query_map_weights(netuid=10)[1]
        weight_dict = {}
        for uid, weight in weights:  # type: ignore
            if uid not in weight_dict:
                weight_dict[uid] = weight
        return weight_dict

    def parse_stake(self):
        """
        A function that parses stake information and returns the result from comx.query_map_stake with netuid 10.
        """
        logger.info("\nParsing stake")
        return comx.query_map_stake(netuid=10)

    def check_weights(self, selfuid, weights, addresses):
        """
        Checks for unranked weights and assigns a default weight of 30 to the missing weights.

        Parameters:
            selfuid: The unique identifier of the validator.
            weights: A dictionary mapping UID to weight.
            addresses: A dictionary containing addresses of validators.

        Returns:
            dict: A dictionary with updated weights.
        """
        logger.info("\nChecking for unranked weights")
        for uid, _ in addresses.items():
            if uid not in weights and uid != selfuid:
                weights[uid] = 30

        return weights

    def parse_keys(self):
        """
        A function that parses keys and returns the result from comx.query_map_key with netuid 10.
        """
        logger.info("\nParsing keys")
        return comx.query_map_key(netuid=10)

    def scale_numbers(self, numbers):
        """
        A function that scales a list of numbers between 0 and 1 based on their minimum and maximum values.

        Parameters:
            self: The instance of the class.
            numbers: A list of numbers to be scaled.

        Returns:
            list: A list of scaled numbers between 0 and 1.
        """
        logger.info("\nScaling numbers")
        min_value = min(numbers)
        max_value = max(numbers)
        return [(number - min_value) / (max_value - min_value) for number in numbers]

    def list_to_dict(self, list):
        """
        A function that converts a list into a dictionary where the index of each element is the key.

        Parameters:
            self: The instance of the class.
            list: A list to be converted into a dictionary.

        Returns:
            dict: A dictionary where the keys are the indices of the list elements and the values are the elements themselves.
        """
        return {i: list[i] for i in range(len(list))}

    def scale_dict_values(self, dictionary):
        """
        A function that scales the values of a dictionary between 0 and 1 based on their minimum and maximum values.

        Parameters:
            self: The instance of the class.
            dictionary: A dictionary with numeric values to be scaled.

        Returns:
            dict: A dictionary with the scaled values between 0 and 1.
        """
        logger.info("\nScaling dictionary values")
        return {
            key: (value - min(dictionary.values()))
            / (max(dictionary.values()) - min(dictionary.values()))
            for key, value in dictionary.items()
        }

    def score_modules(self, weights_dict, staketos_dict, keys_dict, similairity_dict):
        """
        Calculates the scores for modules based on weights, staketos, keys, and similarity values.

        Parameters:
            self: The instance of the class.
            weights_dict (dict): A dictionary containing weights for each module.
            staketos_dict (dict): A dictionary containing staketos for each module.
            keys_dict (dict): A dictionary containing keys for each module.
            similarity_dict (dict): A dictionary containing similarity values for each module.

        Returns:
            dict: A dictionary containing the calculated scores for each module.
        """
        logger.info("\nCalculating scores")
        staketos = {}
        for uid, key in keys_dict.items():
            if key in staketos_dict:
                staketo = staketos_dict[key]
                staketos[uid] = staketo
        scaled_staketos_dict = self.scale_dict_values(staketos)
        scaled_weight_dict = self.scale_dict_values(weights_dict)
        scaled_similairity_dict = self.scale_dict_values(similairity_dict)
        scaled_scores = {}
        for uid in keys_dict.keys():
            
            if uid in scaled_staketos_dict:
                stake = scaled_staketos_dict[uid]
            calculated_score = (
                scaled_weight_dict[uid] * 0.4
                + stake * 0.2
                + scaled_similairity_dict[uid] * 0.2
            ) 
            scaled_scores[uid] = calculated_score
            logger.debug(f"UID: {uid}\nScore: {calculated_score}")
            
        scaled_score = self.scale_dict_values(scaled_scores)
        print(scaled_score)
        return scaled_score
