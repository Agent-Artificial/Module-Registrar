import random
import json
import time

from pathlib import Path
from loguru import logger

from communex._common import get_node_url
from communex.compat.key import Keypair
from communex.client import CommuneClient


VOTE_RANGE = 544
SELFUIDS = [5, 45, 51, 477, 478, 1, 44]
NETUID = 10

miners = {
    "44": {
        "key": "5HVnjqKjcvQX1a65gczD8XcaKNiPYPAimyiaaMUf2cWxG775",
        "name": "eden.Miner_3",
        "address": "24.66.238.82:10003",
    },
    "385": {
        "key": "5H9VzKZqw1wWfxo6Z22q7saqywzaqaLmjTscWH35QLrxgBcY",
        "name": "kren.Miner_1",
        "address": "75.157.35.90:10050",
    },
    "477": {
        "key": "5GH2nE5C88a3eUFGNyFzgkPTRsF4M89nawsQfUYXmUVfaJet",
        "name": "admin.Miner_1",
        "address": "75.157.35.90:8051",
    },
    "478": {
        "key": "5GsfkENPsAakvQ5aV9vji9sDBPpAZSALewkpbWdcfJasaBg7",
        "name": "admin.Miner_2",
        "address": "75.157.35.90:8052",
    },
    "0": {
        "key": "5EJKwpcNneo7Jutnktod4gWeGbXKgriY7RrxqSE7QMa32u4M",
        "name": "vali::eden00",
        "address": "194.102.185.52",
    },
    "4": {
        "key": "5En6afaDn1xbcYMWLoVJWnnJZatFaQu39F6Pv7zNXKqrCjX5",
        "name": "eden.Miner_1",
        "address": "24.66.238.82:10001",
    },
    "5": {
        "key": "5DRehMw43SRj93wHieGV1QS2fZBwNvHpRgkmkxWotfQns5Xy",
        "name": "eden.Validator_2",
        "address": "24.66.238.82:10020",
    },
    "292": {
        "key": "5F7YoJfytfazmicwiUQScuKsyBo36yns3VcQ8H1XSup2WR5j",
        "name": "quackers.HeComes0",
        "address": "75.157.35.90:10000",
    },
    "293": {
        "key": "5F7FDsAe6uwxMz4h92REQAgYNwiibDC5ZRq7WRF65y58qr6D",
        "name": "quackers.HeComes1",
        "address": "75.157.35.90:10001",
    },
    "294": {
        "key": "5HEqnLow1Cv7w4B42FHmgLhu8A52CQRdUKbMAgiqJFDAyPVb",
        "name": "quackers.HeComes2",
        "address": "75.157.35.90:10002",
    },
    "295": {
        "key": "5DHqts1BN8XvR5nU7jJk8rpXanN9vu85kA3tLsKA35qFA9xu",
        "name": "quackers.HeComes3",
        "address": "75.157.35.90:10003",
    },
    "296": {
        "key": "5FF7Ua4oMqRDkShSRFYxq2g3Twp5M1CrQovUVE4esXdxUQAF",
        "name": "quackers.HeComes4",
        "address": "75.157.35.90:10004",
    },
    "297": {
        "key": "5FA3FT2A7GMLbdAiw71wTy2Lco6EzAQdoQaFkVQLcobtT2rt",
        "name": "quackers.HeComes5",
        "address": "75.157.35.90:10005",
    },
    "298": {
        "key": "5D52gbf7K8RDXhAzySYgwdLZGnaHX5gYRvDsgnL3N8wTXf6C",
        "name": "quackers.HeComes6",
        "address": "75.157.35.90:10006",
    },
    "43": {
        "key": "5CAG7oQkWpLng4mEV924FA3epLUudnu3jJkjiqHC69UZAX9q",
        "name": "eden.Miner_2",
        "address": "24.66.238.82:10002",
    },
    "299": {
        "key": "5CSwthC3uDbcbywSd7DMtmgoVqM69oeLBPhuUw9bhF5SneD9",
        "name": "quackers.HeComes7",
        "address": "75.157.35.90:10007",
    },
    "300": {
        "key": "5DSVoNzPp9NggZZarjk4uK7pDi9YJNvhyAGWAoku1bANvhJu",
        "name": "quackers.HeComes8",
        "address": "75.157.35.90:10008",
    },
    "45": {
        "key": "5CP77hmJ8qgwBZyacTY8pFXK5k9fBsHD7P7Hgf3kNxRuJM87",
        "name": "eden.Miner_4",
        "address": "24.66.238.82:10004",
    },
    "46": {
        "key": "5EqZFmP6PDFqVbMxRwEkHGuFBmn8iJoix9rdzi3tWEGBs9vs",
        "name": "eden.Miner_5",
        "address": "24.66.238.82:10005",
    },
    "47": {
        "key": "5CDqxKphZZDyCUYyb7rChm7EmivAHU97fGTAUNvYLTVW9x1z",
        "name": "eden.Miner_6",
        "address": "24.66.238.82:10006",
    },
    "48": {
        "key": "5GgxG78qrqzk84bxBTYEfhBQaxwFTqMLgthoQZnnyYbfxhwc",
        "name": "eden.Miner_7",
        "address": "24.66.238.82:10007",
    },
    "49": {
        "key": "5GEcL3pdosixADiKez74emr88yH5k7ojk3Cb3VVHS3Uyupoi",
        "name": "eden.Miner_8",
        "address": "24.66.238.82:10008",
    },
    "50": {
        "key": "5HVXivKUtYkrzMGyCY4GbWgFQBJjcL2jpkeHYsuLCeTe7kSA",
        "name": "eden.Miner_9",
        "address": "24.66.238.82:10009",
    },
    "51": {
        "key": "5Dqz1mcuBjKvXLRoPgNikSambGDCMaUPMmbsx8vkXfRAKLQU",
        "name": "eden.Validator_0",
        "address": "24.66.238.82:10000",
    },
    "1": {
        "key": "5FjyW3vcB8MkDh19JV88dVLGP6wQEftJC6nXUEobQmdZc6PY",
        "name": "eden.Validator_1",
        "address": "24.66.238.82:10000",
    },
}


comx = CommuneClient(get_node_url())


def get_keys(module_path):
    logger.info("get_keys")
    key_path = Path(f"~/.commune/key/{module_path}.json").expanduser().resolve()
    key_data = json.loads(key_path.read_text("utf-8"))["data"]

    ss58_address = json.loads(key_data)["ss58_address"]
    public_key = json.loads(key_data)["public_key"]
    private_key = json.loads(key_data)["private_key"]

    return Keypair(
        public_key=public_key, private_key=private_key, ss58_address=ss58_address
    )


def get_weights(address_dict):
    logger.info("Getting weights")
    final_weights = []
    uids = []
    chosen_uids = []
    tracker = {}
    for miner_uid in miners.keys():
        if miner_uid == "1":
            continue
        uid = int(miner_uid)
        wgt = 30 + random.choice(range(-1, 1))
        final_weights.append(wgt)
        chosen_uids.append(uid)
    for uid, address in address_dict.items():
        host = address.split(":")[0]
        if host in ["None", "127.0.0.1", "0.0.0.0"] or uid in chosen_uids:
            continue
        uids.append(uid)
    random.shuffle(uids)
    while len(chosen_uids) <= 419:
        for uid in uids:
            address = address_dict[uid]
            chosen_uids.append(uid)
            weight = 30 + random.choice(range(-2, 2))
            if address not in tracker:
                tracker[address] = 1
            if address in tracker:
                tracker[address] += 1
            if tracker[address] > 9:
                penalty = tracker[address] - 9
                weight = weight - penalty
            final_weights.append(weight)

            if len(final_weights) >= 419:
                break
    return chosen_uids, final_weights


def vote(address_dict, key_dict, stake_dict):
    while True:
        logger.info("Starting vote cycle")
        address_dict = comx.query_map_address(NETUID)
        uids, weights = get_weights(address_dict)
        uids, weights = scale_by_stake(weights, uids, key_dict, stake_dict)

        for selfuid in SELFUIDS:
            name = miners[str(selfuid)]["name"]
            logger.info(f"Voting with: {name}")
            keypair = get_keys(name)
            try:
                result = comx.vote(keypair, uids, weights, NETUID)
            except Exception as e:  # type: ignore
                logger.error(e)
            logger.debug(f"Complete: {result.finalized}")
            time.sleep(45)


def scale_by_stake(weights_list, uid_list, key_dict, stake_dict):
    logger.info("Adding stake modifier")
    uids = []
    weights = []
    for i, uid in enumerate(uid_list):
        weight = weights_list[i]
        key = key_dict[uid]
        if key in stake_dict:
            stake = stake_dict[key]
            weight = int(weight + stake / 1000000000000)
        weight = min(weight, 40)
        uids.append(uid)
        weights.append(weight)
        logger.debug(f"{uid}: {weight}")

    logger.debug(len(uids))
    logger.debug(len(weights))
    return uids, weights


def main():
    logger.info("Starting main")
    key_dict = comx.query_map_key(NETUID)
    address_dict = comx.query_map_address(NETUID)
    stake_dict = comx.query_map_stake(NETUID)
    vote(address_dict, key_dict, stake_dict)


if __name__ == "__main__":
    main()
