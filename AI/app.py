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
import socket
import sys
import pickle 
from Scoreboard import Scoreboard

server_address = ('192.168.168.167', 8500)  # Connect to RPi (or other server) on ip ... and port ... (the port is set in server.py)
# the ip address can also be the WiFi ip of your RPi, but this can change. You can print your WiFi IP on your LCD? (if needed)

# Global vars for use in methods/threads
client_socket = None
receive_thread = None
shutdown_flag = threading.Event() # see: https://docs.python.org/3/library/threading.html#event-objects

model = YOLO(r".\AI\runs\pose\train6\weights\best.pt")
#model = YOLO("yolov8n-pose.pt")

def setup_socket_client():
    global client_socket, receive_thread
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket instance
    client_socket.connect(server_address) # connect to specified server
    print("Connected to server")

def extract_audio(video_path, audio_path="./Files/Audio/"):
    filename = f"{audio_path}{Path(video_path).name[:-4]}.mp3"
    if not Path(filename).exists():
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(filename = filename, fps = 48000)        
    return filename

def preprocesss_video(video_path):
    try:
        cap_video = cv2.VideoCapture(video_path)
        # Specifications of the desired video output
        filename = Path(video_path).name
        output_file = f'./Files/Preprocessed_videos/{filename}'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        frame_rate = cap_video.get(cv2.CAP_PROP_FPS)

        screen_width = 1920
        screen_height = 1080

        # Creating a csv-file to save the keypoints to reuse them if needed
        filepath = f'./Files/Preprocessed_videos/{filename[:-4]}.pkl'
        file = open(filepath, "wb")

        # Creating the VideoWriter object
        out = cv2.VideoWriter(output_file, fourcc, frame_rate, (screen_width, screen_height))

        keypoints = []
        print("Preparing the files... Please wait!")
        while cap_video.isOpened():
            ret_video, frame_video = cap_video.read()

            if not ret_video:
                break

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
            
            results_video = model.predict(frame_video, verbose = False)

            frame_video = results_video[0].plot()
            out.write(frame_video)
            keypoints.append(results_video[0].keypoints)
            # file.write(f"{results_video[0].keypoints}\n")
        pickle.dump(keypoints, file)
        return output_file, filepath
    
    finally:
        file.close()
        out.release()
        cap_video.release()

def capture_and_display(video_path, audio_path, keypoints_pkl, window_name, webcam_index=0, webcam_width=712, webcam_height=400):
    try:
        # Playing the audio
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        # Loading the file 
        file = open(keypoints_pkl, "rb")
        list_keypoints_video = pickle.load(file)

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

        # Creating a list for calculating the average performance score and a counter so that i do not calculate the similarity score too often
        performance_score = []
        i = 0

        while cap_video.isOpened() and cap_webcam.isOpened():
            # Get the current time of the audio playback
            audio_time = pygame.mixer.music.get_pos() / 1000.0  # Convert milliseconds to seconds
            if audio_time < 0:
                break

            # Calculate the frame number corresponding to the audio time
            frame_number = int(audio_time * fps)
            # print("FPS:",fps, "Frame number:", frame_number, "Audio time:", audio_time) #=> debugging purposes

            # Set the video capture to the corresponding frame number
            cap_video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            # Read the frames
            ret_video, frame_video = cap_video.read()
            ret_webcam, frame_webcam = cap_webcam.read()

            if not ret_video:
                pygame.mixer.music.stop()
                break
            if not ret_webcam:
                break

            # Mirroring the webcam feed 
            frame_webcam = cv2.flip(frame_webcam, 1)

            # Resizing the webcam frame
            frame_webcam = cv2.resize(frame_webcam, (webcam_width, webcam_height))

            # Getting the predictions from the model
            results_webcam = model.predict(frame_webcam, verbose = False)

            # Position the webcam frame in the bottom right corner
            x_offset = screen_width - webcam_width
            y_offset = screen_height - webcam_height

            # Overlay the webcam frame on the main video frame and display the window
            frame_video[y_offset:(y_offset+webcam_height), x_offset:(x_offset+webcam_width)] = results_webcam[0].plot()
            cv2.imshow(window_name, frame_video)
            
            if i%12 == 0: # Send some data every 12 iterations            
                # Computing the similarity score:
                # Getting the keypoints
                keypoints_video = list_keypoints_video[frame_number-1]
                keypoints_webcam = results_webcam[0].keypoints

                if (keypoints_webcam.xy.cpu().numpy().size != 0) and (keypoints_video.xy.cpu().numpy().size != 0):
                    # Reshaping the arrays
                    person_webcam = keypoints_webcam[round(keypoints_webcam.data.shape[0]/2)-1].xyn.reshape(1,-1).cpu().numpy()
                    person_video = keypoints_video[round(keypoints_video.data.shape[0]/2)-1].xyn.reshape(1,-1).cpu().numpy()

                    difference = 0

                    # Calculating the differences between normalized keypoints
                    for i in range(34):
                        difference += (10*abs(person_video[0][i]-person_webcam[0][i]))**2*100 # Incorporating second degree

                    # Adding penalty for when most keypoints are not visible
                    if person_webcam[np.nonzero(person_webcam)].size <= 14:
                        score = 0
                    else:
                        score = 1000 - (difference/34) 
                        if score < 0:
                            score = 0
                    performance_score.append(int(score))  

                else: 
                    score = 0
                client_socket.sendall(str(round(score)).encode())
                # print("Score:", int(score)) # debugging purposes
            i += 1

            if cv2.waitKey(int(fps)) & 0xFF == ord('q'):
                pygame.mixer.music.stop()
                break

    # Releasing resources
    finally:
        file.close()
        cap_video.release()
        cap_webcam.release()
        cv2.destroyAllWindows()
        if len(performance_score) != 0:
            final_score = int(sum(performance_score)/len(performance_score))
            if final_score != 0:
                write_to_file(final_score, video_path)
        else:
            final_score = 0
        client_socket.sendall(str(final_score).encode())

def write_to_file(final_score: int, video_path: str): 
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

    content += f"{final_score},{str(choreography_name)[2:-4]},{time_to_write}\n"
    file.write(content)
    file.close()

def navigation():
    print("\n1. Play")
    print("2. Scoreboard")
    print("3. Quit\n")
    try:
        user_input = int(input("\nEnter the option number [1/2/3]:>"))
    except Exception:
        raise ValueError("\nThere is no such option... Try again!")
    if user_input in range(1,4):
        return user_input
    else:
        raise ValueError("\nThere is no such option... Try again!")

def menu():
    dir_list = os.listdir("./Files/Dance_routines/")
    for i in range(len(dir_list)):
        print(f"{i+1}. {dir_list[i]}")
    try:
        user_input = int(input("\nEnter the number of the choreography you want to dance to:>\n"))
    except Exception:
        raise ValueError("\nPlease enter a NUMBER")
    if user_input <= len(dir_list):
        return dir_list[user_input-1]
    else:
        raise ValueError("\nThe number you entered does not correspond to any video in the library...")
  
def main():
    global client_socket, receive_thread
    setup_socket_client()
    try:
        print("\n Welcome to the dancing game!")
        while True:
            try:
                option = navigation()
                if option == 1:
                    try:
                        choreography_name = menu()
                    except ValueError as ex:
                        print(ex)
                        pass # the loop continues
                    
                    print("TIP: If you want to stop playing the video at any given time, press [q].")

                    video_path = f"./Files/Dance_routines/{choreography_name}"
                    print("Playing: {}".format(choreography_name[:-4]))

                    filename = f"./Files/Preprocessed_videos/{choreography_name}"
                    keypoints = f"./Files/Preprocessed_videos/{choreography_name[:-4]}.pkl"

                    if not (Path.is_file(Path(filename)) and Path.is_file(Path(keypoints))):
                        filename, keypoints = preprocesss_video(video_path = video_path)
                    capture_and_display(video_path = filename, audio_path = extract_audio(video_path), keypoints_pkl=keypoints, window_name='Dancing Game', webcam_index=0)

                    print("\nYour final score is displayed on the LCD!")
                    user_input = input("\nPress Y if you want to play more:>")
                    if user_input.lower() != "y":
                        break
                elif option == 2:
                    Scoreboard.print_top_k_scores(10)
                elif option == 3:
                    break
            except ValueError as ex:
                print(ex)
                pass
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        shutdown_flag.set()
    finally:
        client_socket.close()
        print("\nExiting the application... Bye!")

if __name__ == "__main__":
    main()