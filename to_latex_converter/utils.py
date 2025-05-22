import logging
import os
import sys
from pathlib import Path

import omegaconf
from omegaconf import OmegaConf
def init_basic_logger(
    name: str,
    level: int = None,
    with_tqdm: bool = False,
    file_handler: Path = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if level is None:
        logger.setLevel(os.environ.get("LOGLEVEL", "DEBUG").upper())
    else:
        logger.setLevel(level)
    if len(logger.handlers) == 0 and not with_tqdm:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(
            logging.Formatter(fmt="[%(asctime)s: %(levelname)s %(name)s] %(message)s")
        )
        logger.addHandler(handler)
    if file_handler is not None:
        handler = logging.FileHandler(file_handler)
        handler.setFormatter(
            logging.Formatter(fmt="[%(asctime)s: %(levelname)s %(name)s] %(message)s")
        )
        logger.addHandler(handler)
    return logger


def load_config(
    config_path: Path, load_base: bool = True
) -> omegaconf.dictconfig.DictConfig:
    config_folder = config_path.parent
    config = OmegaConf.load(str(config_path))

    # merge config
    if load_base and "base" in config:
        base_configs = config.base
        full_base_config = None
        for base_config_path in base_configs:
            base_config_part = OmegaConf.load(str(config_folder / base_config_path))
            if full_base_config is None:
                full_base_config = base_config_part
            else:
                full_base_config = OmegaConf.merge(base_config_part, full_base_config)
        config = OmegaConf.merge(full_base_config, config)
    return config