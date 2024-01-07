import os 
import json
from functools import partial


def load_json(file_path: str) -> dict:
    file_abs_path = os.path.abspath(file_path)
    with open(file_abs_path) as file_:
        dict_to_return = json.load(file_)
    return dict_to_return


load_commands_json = partial(load_json, file_path='bot_inner_texts/commands.json')
load_states_json = partial(load_json, file_path='bot_inner_texts/states.json')
load_message_texts_json = partial(load_json, file_path='bot_inner_texts/message_texts.json')
