from typing import Tuple, Optional
import gradio

import fan.globals
from fan import wording
from fan.core import limit_resources, conditional_process
from fan.uis.core import get_ui_component
from fan.normalizer import normalize_output_path
from fan.filesystem import is_image, is_video, clear_temp

OUTPUT_IMAGE : Optional[gradio.Image] = None
OUTPUT_VIDEO : Optional[gradio.Video] = None
OUTPUT_START_BUTTON : Optional[gradio.Button] = None
OUTPUT_CLEAR_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global OUTPUT_IMAGE
	global OUTPUT_VIDEO
	global OUTPUT_START_BUTTON
	global OUTPUT_CLEAR_BUTTON

	OUTPUT_IMAGE = gradio.Image(
		label = wording.get('output_image_or_video_label'),
		visible = False
	)
	OUTPUT_VIDEO = gradio.Video(
		label = wording.get('output_image_or_video_label')
	)
	OUTPUT_START_BUTTON = gradio.Button(
		value = wording.get('start_button_label'),
		variant = 'primary',
		size = 'sm'
	)
	OUTPUT_CLEAR_BUTTON = gradio.Button(
		value = wording.get('clear_button_label'),
		size = 'sm'
	)


def listen() -> None:
	output_path_textbox = get_ui_component('output_path_textbox')
	if output_path_textbox:
		OUTPUT_START_BUTTON.click(start, inputs = output_path_textbox, outputs = [ OUTPUT_IMAGE, OUTPUT_VIDEO ])
	OUTPUT_CLEAR_BUTTON.click(clear, outputs = [ OUTPUT_IMAGE, OUTPUT_VIDEO ])


def start(output_path : str) -> Tuple[gradio.Image, gradio.Video]:
	fan.globals.output_path = normalize_output_path(fan.globals.source_paths, fan.globals.target_path, output_path)
	limit_resources()
	conditional_process()
	if is_image(fan.globals.output_path):
		return gradio.Image(value = fan.globals.output_path, visible = True), gradio.Video(value = None, visible = False)
	if is_video(fan.globals.output_path):
		return gradio.Image(value = None, visible = False), gradio.Video(value = fan.globals.output_path, visible = True)
	return gradio.Image(), gradio.Video()


def clear() -> Tuple[gradio.Image, gradio.Video]:
	if fan.globals.target_path:
		clear_temp(fan.globals.target_path)
	return gradio.Image(value = None), gradio.Video(value = None)
