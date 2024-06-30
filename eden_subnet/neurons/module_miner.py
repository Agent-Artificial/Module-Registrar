import time 
from typing import *
import bittensor as bt

from eden_subnet.neurons.bittensor_base.base_miner import BaseMinerNeuron
from eden_subnet.neurons.bittensor_base.base_neuron_config import config, check_config





class ModuleMiner:
    """
    Generic module miner that accepets an inference module to run that kind of inference. This system is based on the plugin archetecture to enable a multi miner, able to miner on multiple subnets with a standardized module to define subnet requirements.
    """
    