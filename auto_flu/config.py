import json
import os


def load_config(config_path: str) -> dict[str, object]:
    """
    Load the config file from the given path.

    :param config_path: Path to the config file.
    :type config_path: str
    :return: The config file as a dict.
    :rtype: dict[str, object]
    """
    with open(config_path, 'r') as f:
        config = json.load(f)

    config['excluded_runs'] = []
    if 'excluded_runs_list' in config and os.path.exists(config['excluded_runs_list']):
        with open(config['excluded_runs_list'], 'r') as f:
            for line in f.readlines():
                config['excluded_runs'].append(line.strip())

    return config
