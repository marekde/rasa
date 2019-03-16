import itertools

import contextlib
import io
from typing import Text, List

import jsonpickle
import os
from yarl import URL

from rasa_core import utils
from rasa_core.domain import Domain
from rasa_core.events import UserUttered, Event
from rasa_core.trackers import DialogueStateTracker
from tests.conftest import DEFAULT_DOMAIN_PATH


def latest_request(mocked, request_type, path):
    return mocked.requests.get((request_type, URL(path)))


def json_of_latest_request(r):
    return r[-1].kwargs["json"]


def tracker_from_dialogue_file(filename: Text, domain: Domain = None):
    dialogue = read_dialogue_file(filename)

    if not domain:
        domain = Domain.load(DEFAULT_DOMAIN_PATH)

    tracker = DialogueStateTracker(dialogue.name, domain.slots)
    tracker.recreate_from_dialogue(dialogue)
    return tracker


def read_dialogue_file(filename: Text):
    return jsonpickle.loads(utils.read_file(filename))


def write_text_to_file(tmpdir: Text, filename: Text, text: Text):
    path = tmpdir.join(filename).strpath
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


@contextlib.contextmanager
def cwd(path: Text):
    CWD = os.getcwd()

    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(CWD)


@contextlib.contextmanager
def mocked_cmd_input(package, text):
    if isinstance(text, str):
        text = [text]

    text_generator = itertools.cycle(text)
    i = package.get_cmd_input

    def mocked_input(*args, **kwargs):
        value = next(text_generator)
        print("wrote '{}' to input".format(value))
        return value

    package.get_cmd_input = mocked_input
    try:
        yield
    finally:
        package.get_cmd_input = i


def user_uttered(text: Text, confidence: float) -> UserUttered:
    parse_data = {'intent': {'name': text, 'confidence': confidence}}
    return UserUttered(text='Random', intent=parse_data['intent'],
                       parse_data=parse_data)


def get_tracker(events: List[Event]) -> DialogueStateTracker:
    return DialogueStateTracker.from_events("sender", events, [], 20)
