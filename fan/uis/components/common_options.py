from typing import Optional, List
import gradio

import fan.globals
from fan import wording
from fan.uis import choices as uis_choices

COMMON_OPTIONS_CHECKBOX_GROUP : Optional[gradio.Checkboxgroup] = None


def render() -> None:
	global COMMON_OPTIONS_CHECKBOX_GROUP

	value = []
	if fan.globals.keep_fps:
		value.append('keep-fps')
	if fan.globals.keep_temp:
		value.append('keep-temp')
	if fan.globals.skip_audio:
		value.append('skip-audio')
	if fan.globals.skip_download:
		value.append('skip-download')
	COMMON_OPTIONS_CHECKBOX_GROUP = gradio.Checkboxgroup(
		label = wording.get('common_options_checkbox_group_label'),
		choices = uis_choices.common_options,
		value = value
	)


def listen() -> None:
	COMMON_OPTIONS_CHECKBOX_GROUP.change(update, inputs = COMMON_OPTIONS_CHECKBOX_GROUP)


def update(common_options : List[str]) -> None:
	fan.globals.keep_fps = 'keep-fps' in common_options
	fan.globals.keep_temp = 'keep-temp' in common_options
	fan.globals.skip_audio = 'skip-audio' in common_options
	fan.globals.skip_download = 'skip-download' in common_options
