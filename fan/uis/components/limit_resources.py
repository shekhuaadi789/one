from typing import Optional
import gradio

import fan.globals
import fan.choices
from fan import wording

MAX_MEMORY_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global MAX_MEMORY_SLIDER

	MAX_MEMORY_SLIDER = gradio.Slider(
		label = wording.get('max_memory_slider_label'),
		step = fan.choices.max_memory_range[1] - fan.choices.max_memory_range[0],
		minimum = fan.choices.max_memory_range[0],
		maximum = fan.choices.max_memory_range[-1]
	)


def listen() -> None:
	MAX_MEMORY_SLIDER.change(update_max_memory, inputs = MAX_MEMORY_SLIDER)


def update_max_memory(max_memory : int) -> None:
	fan.globals.max_memory = max_memory if max_memory > 0 else None
