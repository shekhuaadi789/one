from typing import Optional
import gradio

from fan import metadata, wording

ABOUT_BUTTON : Optional[gradio.HTML] = None
DONATE_BUTTON : Optional[gradio.HTML] = None


def render() -> None:
	global ABOUT_BUTTON
	global DONATE_BUTTON

	ABOUT_BUTTON = gradio.Button(
		value = metadata.get('name') + ' ' + metadata.get('version'),
		variant = 'primary',
		link = metadata.get('url')
	)
	DONATE_BUTTON = gradio.Button(
		value = wording.get('donate_button_label'),
		link = 'https://donate.fan.io',
		size = 'sm'
	)
