import cv2
import pygame
from moviepy.editor import VideoFileClip
from ultralytics import YOLO
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import numpy as np
from pathlib import Path
import os
from datetime import datetime
import time
import threading
from queue import Queue
from BLE_client import run

model = YOLO(r".\AI\runs\pose\train5\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train4\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train3\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train2\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train\weights\best.pt")
#model = YOLO("C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/tests/first_test/runs/pose/train12/weights/best.pt")
#model = YOLO("yolov8n-pose.pt")

# Creating two Queues for communication between threads.
tx_q = Queue()
rx_q = Queue()

targetDeviceName=None
targetDeviceMac="D8:3A:DD:D9:6E:8E"

def init_ble_thread():
    # Creating a new thread for running a function 'run' with specified arguments.
    ble_client_thread = threading.Thread(target=run, args=(
        rx_q, tx_q, targetDeviceName, targetDeviceMac), daemon=True)
    # Starting the thread execution.
    ble_client_thread.start()

def extract_audio(video_path, audio_path="./Files/Audio/"):
    filename = f"{audio_path}{Path(video_path).name}.mp3"
    if not Path(filename).exists():
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(filename = filename, fps = 48000)        
    return filename

def capture_and_display(video_path, audio_path, window_name, webcam_index=0, webcam_width=620, webcam_height=480):
    # Initialize Pygame for audio playback
    cap_video = cv2.VideoCapture(video_path)
    cap_webcam = cv2.VideoCapture(webcam_index)

    # Set the screen width and height
    screen_width = 1920
    screen_height = 1080

    # Get the frame rate of the main video
    fps = cap_video.get(cv2.CAP_PROP_FPS)

    # Make the application run in a full window, full-screen mode
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Playing the audio
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    
    # Creating a list for calculating the average performance score
    performance_score = []

    while cap_video.isOpened() and cap_webcam.isOpened():
        start = time.time()
        # Get the current time of the audio playback
        audio_time = pygame.mixer.music.get_pos() / 1000.0  # Convert milliseconds to seconds

        # Calculate the frame number corresponding to the audio time
        frame_number = int(audio_time * fps)
        print("FPS:",fps, "Frame number:", frame_number, "Audio time:", audio_time)

        # Set the video capture to the corresponding frame number
        cap_video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frames
        ret_video, frame_video = cap_video.read()
        ret_webcam, frame_webcam = cap_webcam.read()

        if not ret_video:
            break
        if not ret_webcam:
            frame_webcam = cv2.imread('path_to_placeholder_image.jpg')  # Placeholder image if webcam feed fails

        # Mirroring the webcam feed 
        frame_webcam = cv2.flip(frame_webcam, 1)

        # Resizing the webcam frame
        frame_webcam = cv2.resize(frame_webcam, (webcam_width, webcam_height))

        # Resizing the video to display properly on full screen
        if (frame_video.shape[1]> frame_video.shape[0]):
            frame_video = cv2.resize(frame_video, (screen_width, screen_height))
        # For vertical videos:
        else:
            magnifier_ratio = screen_height / int(frame_video.shape[0])
            width = round(magnifier_ratio* int(frame_video.shape[1]))
            padding_side = (screen_width-width)/2      
            frame_video = cv2.resize(frame_video, (width, screen_height))
            padding_side = round((screen_width - frame_video.shape[1])/2)
            frame_video = cv2.copyMakeBorder(frame_video, 0, 0, padding_side, padding_side, cv2.BORDER_CONSTANT) # Adding the padding for keepint the ratio of vertical videos

        # Getting the predictions from the model
        results_video = model(frame_video)
        results_webcam = model(frame_webcam)
        frame_video = results_video[0].plot()

        # Position the webcam frame in the bottom right corner
        x_offset = screen_width - webcam_width
        y_offset = screen_height - webcam_height

        # Overlay the webcam frame on the main video frame and display the window
        frame_video[y_offset:(y_offset+webcam_height), x_offset:(x_offset+webcam_width)] = results_webcam[0].plot()
        cv2.imshow(window_name, frame_video)

        # Computing the similarity score:
        # Getting the keypoints
        keypoints_video = results_video[0].keypoints
        keypoints_webcam = results_webcam[0].keypoints

        if (keypoints_webcam.xy.cpu().numpy().size != 0) and (keypoints_video.xy.cpu().numpy().size != 0):
            # Reshaping the arrays
            person_webcam = keypoints_webcam[0].xyn.reshape(1,-1).cpu().numpy()
            person_video = keypoints_video[0].xyn.reshape(1,-1).cpu().numpy()

            difference = 0

            # Calculating the differences between normalized keypoints
            for i in range(34):
                difference += (10*abs(person_video[0][i]-person_webcam[0][i]))**2*100
            print(difference, difference/34)
            # Adding penalty for when most keypoints are not visible
            if person_webcam[np.nonzero(person_webcam)].size <= 14:
                score = 0
            else:
                score = 1000 - (difference/34) # To make sure that the score is not unreasonable high, the difference is divided by 9 (as the number of paired keypoints and a nose) and not 34
                if score < 0:
                    score = 0
            performance_score.append(int(score))  
            tx_q.put(int(score))

        # For debugging
            print("Score:", int(score))

        end = time.time()
        duration_processing = end-start
        print(duration_processing)
        print(duration_processing*fps)

        if cv2.waitKey(int(fps)) & 0xFF == ord('q'):
            break

    # Releasing resources
    cap_video.release()
    cap_webcam.release()
    cv2.destroyAllWindows()
    final_score = int(sum(performance_score)/len(performance_score))
    if final_score != 0:
        write_to_file(final_score, video_path)

def write_to_file(final_score: int, video_path: str): # Be careful about the name of the video
    filepath = "./Files/performance_scores.csv"
    file = open(filepath, "a+")
    content = ""
    if os.path.getsize(filepath) == 0:
        content = "Score,ChoreographyName,DateTime\n"
    time_to_write = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Some exception handling
    try:
        choreography_name = Path(video_path).name.encode("utf-8")
    except Exception:
        print("The program was unable to encode the name. Rename the file for proper displaying.")
        choreography_name = "InvalidName"

    content += f"{final_score},{str(choreography_name)[2:-1]},{time_to_write}\n"
    file.write(content)
    file.close()

# Paths to video and audio files
#video_path = r".\Files\Dance_routines\Doja Cat - So high (Dance Cover) _ Clarkie Capillo.mp4"
video_path = r".\Files\Dance_routines\Doja Cat - Woman _ Gyuri Choreography Beginner Class.mp4"


init_ble_thread()
# Capture and display video from file and webcam
capture_and_display(video_path, extract_audio(video_path), 'Combined Video', webcam_index=0, webcam_height=400, webcam_width=712)
