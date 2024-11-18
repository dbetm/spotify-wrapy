from typing import List, Optional

import cv2
import numpy as np
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

from wrapy.constants import FPS, IMAGE_DURATION_SECS, TRANSTITION_DURATION_SECS


class VideoMaker:
    def __init__(self, image_filepaths: List[str], image_size: tuple):
        self.images = [
            self.__prepare_image(cv2.imread(img), image_size) for img in image_filepaths
        ]

    def __prepare_image(self, img: np.ndarray, dims: tuple) -> np.ndarray:
        """Resize the image to the target dims maintaining their aspect ratio and then
        fill the the remaining space with black color."""
        height, width = img.shape[:2]
        target_height = dims[0]
        target_width = dims[1]
        img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)

        scale = min(target_width / width, target_height / height)
        new_width, new_height = int(scale * width), int(scale * height)

        resized_img = cv2.resize(img, (new_width, new_height))

        top = (target_height - new_height) // 2
        bottom = target_height - new_height - top
        left = (target_width - new_width) // 2
        right = target_width - new_width - left

        filling_color = (0, 0, 0)

        resized_img_with_border = cv2.copyMakeBorder(
            resized_img,
            top,
            bottom,
            left,
            right,
            cv2.BORDER_CONSTANT,
            value=filling_color,
        )

        return resized_img_with_border

    def make(self, output_path: str, audio_path: Optional[str] = None) -> None:
        clips = []

        for i in range(len(self.images) - 1):
            prev_img = self.images[i]
            next_img = self.images[i + 1]

            clip = ImageClip(prev_img).set_duration(IMAGE_DURATION_SECS)
            transition = self.__create_transition(prev_img, next_img)

            clips.extend([clip, transition])

        # add the last image without transition
        clips.append(ImageClip(self.images[-1]).set_duration(IMAGE_DURATION_SECS))
        video = concatenate_videoclips(clips)

        # add audio, cut to the video duration
        if audio_path:
            audio = AudioFileClip(audio_path)
            video = video.set_audio(audio.set_duration(video.duration))

        # save video
        video.write_videofile(output_path, fps=FPS)

    def __create_transition(self, prev_img: np.ndarray, next_img: np.ndarray):
        transition_frames = int(TRANSTITION_DURATION_SECS * FPS)
        transition_video = []

        for i in range(transition_frames):
            alpha = i / transition_frames
            frame = cv2.addWeighted(prev_img, 1 - alpha, next_img, alpha, 0)
            transition_video.append(ImageClip(frame).set_duration(1 / FPS))

        return concatenate_videoclips(transition_video)
