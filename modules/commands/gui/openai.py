import queue
import time

import openai

from modules.api.openai import send_gpt_completion_request
from modules.logs import get_logger

main_logger = get_logger("main")
gui_logger = get_logger("gui")

GPT3_PROMPTS_QUEUE: queue.Queue = queue.Queue()


def handle_gpt3(command, shared_dict):
    prompt = command.removeprefix("gpt3 ").strip()
    GPT3_PROMPTS_QUEUE.put(prompt)


def gpt3_cmd_handler() -> None:
    while True:
        if GPT3_PROMPTS_QUEUE.qsize() != 0:
            prompt = GPT3_PROMPTS_QUEUE.get()
            try:
                response = send_gpt_completion_request(
                    [{"role": "user", "content": prompt}],
                    "admin",
                    model="gpt-3.5-turbo",
                )
                gui_logger.info(f"GPT3> {response}")
            except openai.error.RateLimitError:
                gui_logger.warning("Rate Limited! Try again later.")
            except Exception as e:
                main_logger.error(f"Unhandled exception from request from gui. [{e}]")
        else:
            time.sleep(2)
