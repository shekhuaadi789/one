from typing import Optional, Generator, Deque
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import os
import platform
import subprocess
import cv2
import gradio
from tqdm import tqdm

import fan.globals
from fan import logger, wording
from fan.content_analyser import analyse_stream
from fan.typing import Frame, Face
from fan.face_analyser import get_average_face
from fan.processors.frame.core import get_frame_processors_modules
from fan.ffmpeg import open_ffmpeg
from fan.vision import normalize_frame_color, read_static_images
from fan.uis.typing import StreamMode, WebcamMode
from fan.uis.core import get_ui_component

WEBCAM_CAPTURE : Optional[cv2.VideoCapture] = None
WEBCAM_IMAGE : Optional[gradio.Image] = None
WEBCAM_START_BUTTON : Optional[gradio.Button] = None
WEBCAM_STOP_BUTTON : Optional[gradio.Button] = None


def get_webcam_capture() -> Optional[cv2.VideoCapture]:
	global WEBCAM_CAPTURE

	if WEBCAM_CAPTURE is None:
		if platform.system().lower() == 'windows':
			webcam_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
		else:
			webcam_capture = cv2.VideoCapture(0)
		if webcam_capture and webcam_capture.isOpened():
			WEBCAM_CAPTURE = webcam_capture
	return WEBCAM_CAPTURE


def clear_webcam_capture() -> None:
	global WEBCAM_CAPTURE

	if WEBCAM_CAPTURE:
		WEBCAM_CAPTURE.release()
	WEBCAM_CAPTURE = None


def render() -> None:
	global WEBCAM_IMAGE
	global WEBCAM_START_BUTTON
	global WEBCAM_STOP_BUTTON

	WEBCAM_IMAGE = gradio.Image(
		label = wording.get('webcam_image_label')
	)
	WEBCAM_START_BUTTON = gradio.Button(
		value = wording.get('start_button_label'),
		variant = 'primary',
		size = 'sm'
	)
	WEBCAM_STOP_BUTTON = gradio.Button(
		value = wording.get('stop_button_label'),
		size = 'sm'
	)


def listen() -> None:
	start_event = None
	webcam_mode_radio = get_ui_component('webcam_mode_radio')
	webcam_resolution_dropdown = get_ui_component('webcam_resolution_dropdown')
	webcam_fps_slider = get_ui_component('webcam_fps_slider')
	if webcam_mode_radio and webcam_resolution_dropdown and webcam_fps_slider:
		start_event = WEBCAM_START_BUTTON.click(start, inputs = [ webcam_mode_radio, webcam_resolution_dropdown, webcam_fps_slider ], outputs = WEBCAM_IMAGE)
	WEBCAM_STOP_BUTTON.click(stop, cancels = start_event)
	source_image = get_ui_component('source_image')
	if source_image:
		for method in [ 'upload', 'change', 'clear' ]:
			getattr(source_image, method)(stop, cancels = start_event)


def start(webcam_mode : WebcamMode, resolution : str, fps : float) -> Generator[Frame, None, None]:
	fan.globals.face_selector_mode = 'one'
	fan.globals.face_analyser_order = 'large-small'
	source_frames = read_static_images(fan.globals.source_paths)
	source_face = get_average_face(source_frames)
	stream = None
	if webcam_mode in [ 'udp', 'v4l2' ]:
		stream = open_stream(webcam_mode, resolution, fps) # type: ignore[arg-type]
	webcam_width, webcam_height = map(int, resolution.split('x'))
	webcam_capture = get_webcam_capture()
	if webcam_capture and webcam_capture.isOpened():
		webcam_capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # type: ignore[attr-defined]
		webcam_capture.set(cv2.CAP_PROP_FRAME_WIDTH, webcam_width)
		webcam_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, webcam_height)
		webcam_capture.set(cv2.CAP_PROP_FPS, fps)
		for capture_frame in multi_process_capture(source_face, webcam_capture, fps):
			if webcam_mode == 'inline':
				yield normalize_frame_color(capture_frame)
			else:
				try:
					stream.stdin.write(capture_frame.tobytes())
				except Exception:
					clear_webcam_capture()
				yield None


def multi_process_capture(source_face : Face, webcam_capture : cv2.VideoCapture, fps : float) -> Generator[Frame, None, None]:
	with tqdm(desc = wording.get('processing'), unit = 'frame', ascii = ' =', disable = fan.globals.log_level in [ 'warn', 'error' ]) as progress:
		with ThreadPoolExecutor(max_workers = fan.globals.execution_thread_count) as executor:
			futures = []
			deque_capture_frames : Deque[Frame] = deque()
			while webcam_capture and webcam_capture.isOpened():
				_, capture_frame = webcam_capture.read()
				if analyse_stream(capture_frame, fps):
					return
				future = executor.submit(process_stream_frame, source_face, capture_frame)
				futures.append(future)
				for future_done in [ future for future in futures if future.done() ]:
					capture_frame = future_done.result()
					deque_capture_frames.append(capture_frame)
					futures.remove(future_done)
				while deque_capture_frames:
					progress.update()
					yield deque_capture_frames.popleft()


def stop() -> gradio.Image:
	clear_webcam_capture()
	return gradio.Image(value = None)


def process_stream_frame(source_face : Face, temp_frame : Frame) -> Frame:
	for frame_processor_module in get_frame_processors_modules(fan.globals.frame_processors):
		if frame_processor_module.pre_process('stream'):
			temp_frame = frame_processor_module.process_frame(
				source_face,
				None,
				temp_frame
			)
	return temp_frame


def open_stream(stream_mode : StreamMode, resolution : str, fps : float) -> subprocess.Popen[bytes]:
	commands = [ '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', resolution, '-r', str(fps), '-i', '-' ]
	if stream_mode == 'udp':
		commands.extend([ '-b:v', '2000k', '-f', 'mpegts', 'udp://localhost:27000?pkt_size=1316' ])
	if stream_mode == 'v4l2':
		try:
			device_name = os.listdir('/sys/devices/virtual/video4linux')[0]
			if device_name:
				commands.extend([ '-f', 'v4l2', '/dev/' + device_name ])
		except FileNotFoundError:
			logger.error(wording.get('stream_not_loaded').format(stream_mode = stream_mode), __name__.upper())
	return open_ffmpeg(commands)
