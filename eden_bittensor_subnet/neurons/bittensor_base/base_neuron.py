"""
code taken from https://github.com/Cazure8/transcription-subnet/blob/main/transcription/base/neuron.py
"""

# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 Cazure

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import copy
from typing_extensions import override
from typing import List, Union
import bittensor as bt
from abc import ABC, abstractmethod

from torch import LongTensor, int64, float64, FloatTensor
from pandas._typing import np_ndarray_int64

from eden_bittensor_subnet.neurons.bittensor_base.base_neuron_config import check_config, config, add_args
from eden_bittensor_subnet import __spec_version__
from eden_bittensor_subnet.utilities.time_to_live_cache import ttl_get_block


class Float64:
    def __float64__(self):
        self.__setattr__("dtype", float64)
        
        
class Int64:
    def __int64__(self):
        self.__setattr__("dtype", int64)
        
        
class NDArray:
    def __np_ndarray__(self):
        self.__setattr__("dtype", np_ndarray_int64)


class BaseNeuron(ABC):
    """
    Base class for Bittensor miners. This class is abstract and should be inherited by a subclass. It contains the core logic for all neurons; validators and miners.

    In addition to creating a wallet, subtensor, and metagraph, this class also handles the synchronization of the network state via a basic checkpointing mechanism based on epoch length.
    """

    @classmethod
    def check_config(cls, config: "bt.Config"):
        """Check configuration setup.

        Args:
            config (bt.Config): The config object to check.
        """
        check_config(cls, config)

    @classmethod
    def add_args(cls, parser):
        """
        Adds relevant arguments to the parser for operation.

        Args:
            parser: Parser that will extract arguments to add to the config.
        """
        add_args(cls, parser)

    @classmethod
    @override
    def config(cls):
        """
        Returns the configuration object specific to this miner or validator after adding relevant arguments.
        
        Args: 
            None

        Returns:
            bt.Config: The config object.
        """
        return config(cls)

    subtensor: "bt.subtensor"
    wallet: "bt.wallet"
    metagraph: "bt.metagraph"
    spec_version: int = __spec_version__
    uids: Union[List[Union[int, Int64]], LongTensor, NDArray[Int64]] = LongTensor([])
    weights: Union[List[Union[float, Float64]], FloatTensor, NDArray[Float64]] = FloatTensor([])
    netuid: int = 0

    @property
    def block(self):
        return ttl_get_block(self)

    def __init__(self, starting_config=None):
        base_config = copy.deepcopy(starting_config or BaseNeuron.config())
        self.config = self.config()
        self.config.merge(base_config)
        self.check_config(self.config)

        # Set up logging with the provided configuration and directory.
        bt.logging(config=self.config, logging_dir=self.config.full_path)

        # If a gpu is required, set the device to cuda:N (e.g. cuda:0)
        self.device = self.config.neuron.device

        # Log the configuration for reference.
        bt.logging.info(self.config)

        # Build Bittensor objects
        # These are core Bittensor classes to interact with the network.
        bt.logging.info("Setting up bittensor objects.")

        # The wallet holds the cryptographic key pairs for the miner.
        self.wallet = bt.wallet(config=self.config)
        bt.logging.info(f"Wallet: {self.wallet}")

        # The subtensor is our connection to the Bittensor blockchain.
        self.subtensor = bt.subtensor(config=self.config)
        bt.logging.info(f"Subtensor: {self.subtensor}")

        # The metagraph holds the state of the network, letting us know about other validators and miners.
        self.metagraph = self.subtensor.metagraph(self.config.netuid)
        bt.logging.info(f"Metagraph: {self.metagraph}")

        # Check if the miner is registered on the Bittensor network before proceeding further.
        self.check_registered()

        # Each miner gets a unique identity (UID) in the network for differentiation.
        self.uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
        bt.logging.info(
            f"Running neuron on subnet: {self.config.netuid} with uid {self.uid} using network: {self.subtensor.chain_endpoint}"
        )
        self.step = 0

    @abstractmethod
    async def forward(self, synapse: bt.Synapse) -> bt.Synapse:
        """Main logic for data processing of the miner. Using the term forward from forward pass out of machine learning as the primary data processing step of a neural network."""

    @abstractmethod
    def run(self):
        """Serves the miner in the main loop via api"""
        
    def resync_metagraph(self):
        """
        Syncronizes the network metagraph state with the network at the current block.
        """
        self.metagraph.sync(self.block)
        
    def set_weights(self) -> None:
        """
        Votes for the miners on the subnets by setting the weights, or scores of the miners based on their performance. 
        """
        self.subtensor.set_weights(self.wallet, self.netuid, self.uids, self.weights)

    def sync(self):
        """
        Wrapper for synchronizing the state of the network for the given miner or validator.
        """
        # Ensure miner or validator hotkey is still registered on the network.
        self.check_registered()

        if self.should_sync_metagraph():
            self.resync_metagraph()

        if self.should_set_weights():
            self.set_weights()

        # Always save state.
        self.save_state()

    def check_registered(self):
        # --- Check for registration.
        if not self.subtensor.is_hotkey_registered(
            netuid=self.config.netuid,
            hotkey_ss58=self.wallet.hotkey.ss58_address,
        ):
            bt.logging.error(
                f"Wallet: {self.wallet} is not registered on netuid {self.config.netuid}."
                f" Please register the hotkey using `btcli subnets register` before trying again"
            )
            exit()

    def should_sync_metagraph(self):
        """
        Check if enough epoch blocks have elapsed since the last checkpoint to sync.
        """
        return (
            self.block - self.metagraph.last_update[self.uid]
        ) > self.config.neuron.epoch_length

    def should_set_weights(self) -> bool:
        # Don't set weights on initialization.
        if self.step == 0:
            return False

        # Check if enough epoch blocks have elapsed since the last epoch.
        if self.config.neuron.disable_set_weights:
            return False

        # Define appropriate logic for when set weights.
        return (
            self.block - self.metagraph.last_update[self.uid]
        ) > self.config.neuron.epoch_length

    def save_state(self):
        bt.logging.warning(
            "save_state() not implemented for this neuron. You can implement this function to save model checkpoints or other useful data."
        )

    def load_state(self):
        bt.logging.warning(
            "load_state() not implemented for this neuron. You can implement this function to load model checkpoints or other useful data."
        )
