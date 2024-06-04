import cv2
import pygame
from moviepy.editor import VideoFileClip
from ultralytics import YOLO
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import numpy as np
from pathlib import Path

model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train5\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train4\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train3\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train2\weights\best.pt")
#model = YOLO(r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\2023-2024-projectone-ctai-ViolettaNguyen1\runs\pose\train\weights\best.pt")
#model = YOLO("C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/tests/first_test/runs/pose/train12/weights/best.pt")
#model = YOLO("yolov8n-pose.pt")

def extract_audio(video_path, audio_path="C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/data/audio/"):
    filename = f"{audio_path}{Path(video_path).name}.mp3"
    if not Path(filename).exists():
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(filename = filename, fps = 48000)        
    return filename

def resize_frame(frame, dimensions):
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def capture_and_display(video_path, audio_path, window_name, webcam_index=0, webcam_width=320, webcam_height=240):
    # Initialize Pygame for audio playback
    cap_video = cv2.VideoCapture(video_path)
    cap_webcam = cv2.VideoCapture(webcam_index)

    # Get the dimensions of the main video
    ret, frame = cap_video.read()
    if not ret:
        print("Error: Unable to read the video file.")
        return
    
    screen_width = 1920
    screen_height = 1080

    # Get the frame rate of the main video
    fps = cap_video.get(cv2.CAP_PROP_FPS)

    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    performance_score = []

    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    
    while cap_video.isOpened() and cap_webcam.isOpened():
        # Get the current time of the audio playback
        audio_time = pygame.mixer.music.get_pos() / 1000.0  # Convert milliseconds to seconds

        # Calculate the frame number corresponding to the audio time
        frame_number = int(audio_time * fps)
        print(fps, frame_number)

        # Set the video capture to the corresponding frame number
        cap_video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret_video, frame_video = cap_video.read()
        ret_webcam, frame_webcam = cap_webcam.read()

        if not ret_video:
            break
        if not ret_webcam:
            frame_webcam = cv2.imread('path_to_placeholder_image.jpg')  # Placeholder image if webcam feed fails

        # Mirroring the webcam feed 
        frame_webcam = cv2.flip(frame_webcam, 1)
        # Resize the webcam frame
        frame_webcam_resized = resize_frame(frame_webcam, (webcam_width, webcam_height))
        # ADDITION: resize video
        if (frame_video.shape[1]> frame_video.shape[0]):
            frame_video = resize_frame(frame_video, (1920,1080))
        else:
            magnifier_ratio = 1080 / int(frame_video.shape[0])
            width = round(magnifier_ratio* int(frame_video.shape[1]))
            padding_side = (1920-width)/2      
            frame_video = resize_frame(frame_video, (width, 1080))
            padding_side = round((1920 - frame_video.shape[1])/2)
            frame_video = cv2.copyMakeBorder(frame_video, 0, 0, padding_side, padding_side, cv2.BORDER_CONSTANT)

        results_video = model(frame_video)
        results_webcam = model(frame_webcam_resized)
        frame_video = results_video[0].plot()

        # Position the webcam frame in the bottom right corner
        x_offset = screen_width - webcam_width
        y_offset = screen_height - webcam_height

        # Overlay the webcam frame on the main video frame
        # frame_video[y_offset:y_offset+webcam_height, x_offset:x_offset+webcam_width] = frame_webcam_resized
        # frame_video[y_offset:y_offset+webcam_height, x_offset:x_offset+webcam_width] = frame_webcam_resized
        frame_video[y_offset:y_offset+webcam_height, x_offset:x_offset+webcam_width] = results_webcam[0].plot()
        cv2.imshow(window_name, frame_video)

        keypoints_video = results_video[0].keypoints
        keypoints_webcam = results_webcam[0].keypoints
        # boxes = results[0].boxes
        #print(keypoints)
        array_webcam = keypoints_webcam.xy.cpu().numpy()
        array_video = keypoints_video.xy.cpu().numpy()
        
        if (array_webcam.size != 0) and (array_video.size != 0):
            print(keypoints_video[0].xyn.reshape(1,-1))
            print(keypoints_webcam[0].xyn.reshape(1,-1))
            person_webcam = keypoints_webcam[0].xyn.reshape(1,-1).cpu().numpy()
            person_video = keypoints_video[0].xyn.reshape(1,-1).cpu().numpy()
            difference = 0
            for i in range(34):
                difference += abs(person_video[0][i]-person_webcam[0][i])
            print(difference)
            print(person_webcam[np.nonzero(person_webcam)].size)
            if person_webcam[np.nonzero(person_webcam)].size <= 14:
                score = 0
            else:
                score = 1000 - (difference/17*1000)
            print("Score",score)

            #print(keypoints[0].xy, keypoints[1].xy)
            # person_one = normalize_keypoints(keypoints[0].xyn)
            # person_two = normalize_keypoints(keypoints[1].xyn)
            #print(cosine_similarity(keypoints[0].xy.reshape(17,2), keypoints[1].xy.reshape(17,2))[0][0])
            #print(cosine_similarity(keypoints[0].xy.reshape(1,-1), keypoints[1].xy.reshape(1,-1)))
            # score = (cosine_similarity(person_webcam, person_video)*1000) - penalty
            # if (score<0):
            #     score = 0
            # print(boxes[0].xywh[0]) # 
            # width_box = boxes[0].xywh[0][2] # width of a box
            # difference_x = []
            # difference_y = []
            # for i in range(0,17):
            #     a = keypoints[0].xy[0][i][0]/boxes[0].xywh[0][0]
            #     a1 = keypoints[1].xy[0][i][0]/boxes[1].xywh[0][0]
            #     difference_x.append(abs(a-a1))
            #     b = keypoints[0].xy[0][i][1]/boxes[0].xywh[0][1]
            #     b1 = keypoints[1].xy[0][i][1]/boxes[1].xywh[0][1]
            #     difference_y.append(abs(b-b1))

            # #difference = np.matrix((difference_x,difference_y))
            # difference_x = sum(difference_x)
            # difference_y = sum(difference_y)
            # # difference_y = np.mean(difference_y)
                
            # print(keypoints[0].xy[0][0][1])
            # print(keypoints[0].xy)
            #keypoint_distance = euclidean_distances(keypoints_video[0].xyn.reshape(1,-1), keypoints_webcam[0].xyn.reshape(1,-1), squared=True)
            # if keypoint_distance[0][0] >= 10.0:
            #     score = 0
            # else:
            #     score = 100 - round(keypoint_distance[0][0]*10)

            #score = int(difference_x+difference_y)
            # if score >= 10.0:
            #     score = 0
            # else:
            
            # score = (1 - cosine_similarity(keypoints[1].xyn[0].reshape(1,-1), keypoints[0].xyn[0].reshape(1,-1)))* 100
            # print(np.where(array_webcam == 0,-1, array_webcam)) 
                 
            performance_score.append(int(score))   

        if cv2.waitKey(int(fps)) & 0xFF == ord('q'):
            break

    # Release resources
    cap_video.release()
    cap_webcam.release()
    cv2.destroyAllWindows()
    print("Final score:", (sum(performance_score)/len(performance_score)))

# Paths to video and audio files
#video_path = r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\videos_to_test\KAYDAY X Y CLASS CHOREOGRAPHY VIDEO _ CODE KUNST - XI ft. Lee Hi.mp4"
#video_path = r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\videos_to_test\Watch the OG choreographer slaying KAI's epic Mmmh dance moves!🤩🤩 .mp4"
#video_path = r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\videos_to_test\KISS OF LIFE (키스오브라이프) - 'Nobody Knows' Dance cover  _ 커버댄스  _ 3인안무 .mp4"
#video_path = r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\videos_to_test\Ariana grande - Positions Choreography (choreo by 1million tina boo).mp4"
#video_path = r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\videos_to_test\ROSALÍA - MALAMENTE _ Tina Boo Choreography.mp4"
#video_path = "C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/videos_to_test/😎✨ .mp4"
video_path = "C:/Users/viola/Documents/CTAI/1y/2s/Project 1/project_weeks/videos_to_test/Doja Cat - Need to Know _ Redy Choreography.mp4"
#video_path = r"C:\Users\viola\Documents\CTAI\1y\2s\Project 1\project_weeks\videos_to_test\I don't think anyone can copy her movements🔥😅 .mp4"

# Capture and display video from file and webcam
capture_and_display(video_path, extract_audio(video_path), 'Combined Video', webcam_index=0, webcam_width=620, webcam_height=480)