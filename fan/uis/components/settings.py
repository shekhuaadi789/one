from typing import Optional, List
import gradio

import fan.globals
from fan import wording
from fan.uis import choices
from fan.uis.typing import Update

SETTINGS_CHECKBOX_GROUP : Optional[gradio.Checkboxgroup] = None


def render() -> None:
	global SETTINGS_CHECKBOX_GROUP

	value = []
	if fan.globals.keep_fps:
		value.append('keep-fps')
	if fan.globals.keep_temp:
		value.append('keep-temp')
	if fan.globals.skip_audio:
		value.append('skip-audio')
	SETTINGS_CHECKBOX_GROUP = gradio.Checkboxgroup(
		label = wording.get('settings_checkbox_group_label'),
		choices = choices.settings,
		value = value
	)


def listen() -> None:
	SETTINGS_CHECKBOX_GROUP.change(update, inputs = SETTINGS_CHECKBOX_GROUP, outputs = SETTINGS_CHECKBOX_GROUP)


def update(settings : List[str]) -> Update:
	fan.globals.keep_fps = 'keep-fps' in settings
	fan.globals.keep_temp = 'keep-temp' in settings
	fan.globals.skip_audio = 'skip-audio' in settings
	return gradio.update(value = settings)
