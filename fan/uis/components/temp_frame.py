from typing import Optional, Tuple
import gradio

import fan.globals
import fan.choices
from fan import wording
from fan.typing import TempFrameFormat
from fan.filesystem import is_video
from fan.uis.core import get_ui_component

TEMP_FRAME_FORMAT_DROPDOWN : Optional[gradio.Dropdown] = None
TEMP_FRAME_QUALITY_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global TEMP_FRAME_FORMAT_DROPDOWN
	global TEMP_FRAME_QUALITY_SLIDER

	TEMP_FRAME_FORMAT_DROPDOWN = gradio.Dropdown(
		label = wording.get('temp_frame_format_dropdown_label'),
		choices = fan.choices.temp_frame_formats,
		value = fan.globals.temp_frame_format,
		visible = is_video(fan.globals.target_path)
	)
	TEMP_FRAME_QUALITY_SLIDER = gradio.Slider(
		label = wording.get('temp_frame_quality_slider_label'),
		value = fan.globals.temp_frame_quality,
		step = fan.choices.temp_frame_quality_range[1] - fan.choices.temp_frame_quality_range[0],
		minimum = fan.choices.temp_frame_quality_range[0],
		maximum = fan.choices.temp_frame_quality_range[-1],
		visible = is_video(fan.globals.target_path)
	)


def listen() -> None:
	TEMP_FRAME_FORMAT_DROPDOWN.select(update_temp_frame_format, inputs = TEMP_FRAME_FORMAT_DROPDOWN)
	TEMP_FRAME_QUALITY_SLIDER.change(update_temp_frame_quality, inputs = TEMP_FRAME_QUALITY_SLIDER)
	target_video = get_ui_component('target_video')
	if target_video:
		for method in [ 'upload', 'change', 'clear' ]:
			getattr(target_video, method)(remote_update, outputs = [ TEMP_FRAME_FORMAT_DROPDOWN, TEMP_FRAME_QUALITY_SLIDER ])


def remote_update() -> Tuple[gradio.Dropdown, gradio.Slider]:
	if is_video(fan.globals.target_path):
		return gradio.Dropdown(visible = True), gradio.Slider(visible = True)
	return gradio.Dropdown(visible = False), gradio.Slider(visible = False)


def update_temp_frame_format(temp_frame_format : TempFrameFormat) -> None:
	fan.globals.temp_frame_format = temp_frame_format


def update_temp_frame_quality(temp_frame_quality : int) -> None:
	fan.globals.temp_frame_quality = temp_frame_quality
