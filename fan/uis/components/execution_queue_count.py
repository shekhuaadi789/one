from typing import Optional
import gradio

import fan.globals
import fan.choices
from fan import wording

EXECUTION_QUEUE_COUNT_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global EXECUTION_QUEUE_COUNT_SLIDER

	EXECUTION_QUEUE_COUNT_SLIDER = gradio.Slider(
		label = wording.get('execution_queue_count_slider_label'),
		value = fan.globals.execution_queue_count,
		step = fan.choices.execution_queue_count_range[1] - fan.choices.execution_queue_count_range[0],
		minimum = fan.choices.execution_queue_count_range[0],
		maximum = fan.choices.execution_queue_count_range[-1]
	)


def listen() -> None:
	EXECUTION_QUEUE_COUNT_SLIDER.change(update_execution_queue_count, inputs = EXECUTION_QUEUE_COUNT_SLIDER)


def update_execution_queue_count(execution_queue_count : int = 1) -> None:
	fan.globals.execution_queue_count = execution_queue_count
