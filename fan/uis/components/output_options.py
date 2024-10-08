from typing import Optional, Tuple, List
import tempfile
import gradio

import fan.globals
import fan.choices
from fan import wording
from fan.typing import OutputVideoEncoder
from fan.filesystem import is_image, is_video
from fan.uis.typing import ComponentName
from fan.uis.core import get_ui_component, register_ui_component

OUTPUT_PATH_TEXTBOX : Optional[gradio.Textbox] = None
OUTPUT_IMAGE_QUALITY_SLIDER : Optional[gradio.Slider] = None
OUTPUT_VIDEO_ENCODER_DROPDOWN : Optional[gradio.Dropdown] = None
OUTPUT_VIDEO_QUALITY_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global OUTPUT_PATH_TEXTBOX
	global OUTPUT_IMAGE_QUALITY_SLIDER
	global OUTPUT_VIDEO_ENCODER_DROPDOWN
	global OUTPUT_VIDEO_QUALITY_SLIDER

	OUTPUT_PATH_TEXTBOX = gradio.Textbox(
		label = wording.get('output_path_textbox_label'),
		value = fan.globals.output_path or tempfile.gettempdir(),
		max_lines = 1
	)
	OUTPUT_IMAGE_QUALITY_SLIDER = gradio.Slider(
		label = wording.get('output_image_quality_slider_label'),
		value = fan.globals.output_image_quality,
		step = fan.choices.output_image_quality_range[1] - fan.choices.output_image_quality_range[0],
		minimum = fan.choices.output_image_quality_range[0],
		maximum = fan.choices.output_image_quality_range[-1],
		visible = is_image(fan.globals.target_path)
	)
	OUTPUT_VIDEO_ENCODER_DROPDOWN = gradio.Dropdown(
		label = wording.get('output_video_encoder_dropdown_label'),
		choices = fan.choices.output_video_encoders,
		value = fan.globals.output_video_encoder,
		visible = is_video(fan.globals.target_path)
	)
	OUTPUT_VIDEO_QUALITY_SLIDER = gradio.Slider(
		label = wording.get('output_video_quality_slider_label'),
		value = fan.globals.output_video_quality,
		step = fan.choices.output_video_quality_range[1] - fan.choices.output_video_quality_range[0],
		minimum = fan.choices.output_video_quality_range[0],
		maximum = fan.choices.output_video_quality_range[-1],
		visible = is_video(fan.globals.target_path)
	)
	register_ui_component('output_path_textbox', OUTPUT_PATH_TEXTBOX)


def listen() -> None:
	OUTPUT_PATH_TEXTBOX.change(update_output_path, inputs = OUTPUT_PATH_TEXTBOX)
	OUTPUT_IMAGE_QUALITY_SLIDER.change(update_output_image_quality, inputs = OUTPUT_IMAGE_QUALITY_SLIDER)
	OUTPUT_VIDEO_ENCODER_DROPDOWN.select(update_output_video_encoder, inputs = OUTPUT_VIDEO_ENCODER_DROPDOWN)
	OUTPUT_VIDEO_QUALITY_SLIDER.change(update_output_video_quality, inputs = OUTPUT_VIDEO_QUALITY_SLIDER)
	multi_component_names : List[ComponentName] =\
	[
		'source_image',
		'target_image',
		'target_video'
	]
	for component_name in multi_component_names:
		component = get_ui_component(component_name)
		if component:
			for method in [ 'upload', 'change', 'clear' ]:
				getattr(component, method)(remote_update, outputs = [ OUTPUT_IMAGE_QUALITY_SLIDER, OUTPUT_VIDEO_ENCODER_DROPDOWN, OUTPUT_VIDEO_QUALITY_SLIDER ])


def remote_update() -> Tuple[gradio.Slider, gradio.Dropdown, gradio.Slider]:
	if is_image(fan.globals.target_path):
		return gradio.Slider(visible = True), gradio.Dropdown(visible = False), gradio.Slider(visible = False)
	if is_video(fan.globals.target_path):
		return gradio.Slider(visible = False), gradio.Dropdown(visible = True), gradio.Slider(visible = True)
	return gradio.Slider(visible = False), gradio.Dropdown(visible = False), gradio.Slider(visible = False)


def update_output_path(output_path : str) -> None:
	fan.globals.output_path = output_path


def update_output_image_quality(output_image_quality : int) -> None:
	fan.globals.output_image_quality = output_image_quality


def update_output_video_encoder(output_video_encoder: OutputVideoEncoder) -> None:
	fan.globals.output_video_encoder = output_video_encoder


def update_output_video_quality(output_video_quality : int) -> None:
	fan.globals.output_video_quality = output_video_quality
