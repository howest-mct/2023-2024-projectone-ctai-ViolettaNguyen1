import cv2
import pygame
from threading import Thread
from moviepy.editor import VideoFileClip

def play_audio(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def extract_audio(video_path, audio_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)

def resize_frame(frame, dimensions):
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def capture_and_display(video_path, window_name, webcam_index=0, webcam_width=320, webcam_height=240):
    cap_video = cv2.VideoCapture(video_path)
    cap_webcam = cv2.VideoCapture(webcam_index)

    # Get the dimensions of the main video
    ret, frame = cap_video.read()
    if not ret:
        print("Error: Unable to read the video file.")
        return

    screen_width = frame.shape[1]
    screen_height = frame.shape[0]

    while cap_video.isOpened() and cap_webcam.isOpened():
        ret_video, frame_video = cap_video.read()
        ret_webcam, frame_webcam = cap_webcam.read()

        if not ret_video:
            break
        if not ret_webcam:
            frame_webcam = cv2.imread('path_to_placeholder_image.jpg')  # Placeholder image if webcam feed fails

        # Resize the webcam frame
        frame_webcam_resized = resize_frame(frame_webcam, (webcam_width, webcam_height))

        # Position the webcam frame in the bottom right corner
        x_offset = screen_width - webcam_width
        y_offset = screen_height - webcam_height

        # Overlay the webcam frame on the main video frame
        frame_video[y_offset:y_offset+webcam_height, x_offset:x_offset+webcam_width] = frame_webcam_resized

        cv2.imshow(window_name, frame_video)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap_video.release()
    cap_webcam.release()
    cv2.destroyAllWindows()

# Paths to your video and audio files
video_path = 'C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/data/videos_to_label/nefor_rmb.MP4'
audio_path = 'C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/data/audio/extracted_audio.mp3'

# Extract audio from the video file
extract_audio(video_path, audio_path)

# Initialize pygame in the main thread to avoid issues
pygame.init()

# Start audio playback in a separate thread
audio_thread = Thread(target=play_audio, args=(audio_path,))
audio_thread.start()

# Capture and display video from file and webcam
capture_and_display(video_path, 'Combined Video', webcam_index=0, webcam_width=320, webcam_height=240)

# Ensure the audio thread is completed before exiting
audio_thread.join()

# import cv2
# import numpy as np
# #ffpyplayer for playing audio
# from ffpyplayer.player import MediaPlayer
# video_path="C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/data/videos_to_label/nefor_rmb.MP4"
# def PlayVideo(video_path):
#     player = MediaPlayer(video_path)
#     video=cv2.VideoCapture(video_path)
#     while True:
#         audio_frame, val = player.get_frame()
#         grabbed, frame=video.read()
#         if not grabbed:
#             print("End of video")
#             break
#         if cv2.waitKey(29) & 0xFF == ord("q"):
#             break
#         cv2.imshow("Video", frame)
#         if val != 'eof' and audio_frame is not None:
#             #audio
#             img, t = audio_frame
#     video.release()
#     cv2.destroyAllWindows()

# PlayVideo(video_path)

# import cv2
# import time
# from ffpyplayer.player import MediaPlayer

# def PlayVideo(video_path, audio_path):
#     def get_audio_frame(player):
#         audio_frame, val = player.get_frame()
#         return audio_frame, val
    
#     video = cv2.VideoCapture(video_path)
#     player = MediaPlayer(audio_path)
#     start_time = time.time()

#     while True:
#         grabbed, frame = video.read()
#         if not grabbed:
#             print("End of video")
#             break
        
#         _, val = player.get_frame(show=False)
#         if val == 'eof':
#             break

#         Display video frame
#         cv2.imshow("Video", frame)
#         Get and play audio frame

#         elapsed = (time.time() - start_time) * 1000  # msec
#         play_time = int(video.get(cv2.CAP_PROP_POS_MSEC))
#         sleep = max(1, int(play_time - elapsed))    

#         if cv2.waitKey(sleep) & 0xFF == ord("q"):
#             break

#     player.close_player()
#     video.release()
#     cv2.destroyAllWindows()

# Path to your video file
# video_path = 'C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/data/videos_to_label/nefor_rmb.MP4'
# audio_path = "C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/data/audio/extracted_audio.mp3"
# PlayVideo(video_path, audio_path)

# import time
# class WithMediaPlayer:
#     def __init__(self, audio_file):
#         self.player = MediaPlayer(audio_file)

#     def get_frame(self):
#         _, val = self.player.get_frame(show=False)
#         if val == "eof":
#             return False
#         return True

#     def close(self):
#         if self.player:
#             self.player.close_player()
#             self.player = None


# def main(video_file, audio_file):
#     print(f"{video_file=},{audio_file=}")
#     cap = cv2.VideoCapture(video_file)

#     player = WithMediaPlayer(audio_file)
#     start_time = time.time()

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         if not player.get_frame():
#             break

#         cv2.imshow(video_file, frame)

#         elapsed = (time.time() - start_time) * 1000  # msec
#         play_time = int(cap.get(cv2.CAP_PROP_POS_MSEC))
#         sleep = max(1, int(play_time - elapsed))
#         if cv2.waitKey(sleep) & 0xFF == ord("q"):
#             break

#     player.close()
#     cap.release()
#     cv2.destroyAllWindows()