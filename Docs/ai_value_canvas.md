## 1. **Stakeholders**: 

- ***Who participates***: Me, as the creator of the project; coaches as my mentors; users, who want to learn/copy a dance routine from a video.

- ***Who owns the data***: The users themselves own the output data of the model.

- ***Who takes the action***: Me, as the creator of the program. But after the game is developed no human action is taken after making a prediction. After the pose key points are estimated, the program computes the similarity scores between a pose from an uploaded choreography video and user's pose from camera feed. After the dancing video has ended, the average performance score is computed and displayed on the LCD display. 

- ***Who is impacted by our prediction*:** Beneficiaries of the game are people who want to simply move their body or improve their dancing skills.
## 2. **Need**:

- ***What challenge are we solving*:** Nowadays people are not moving nearly as much as they should. To solve this, I wanted to make a fun game, that would make people stand up and dance. Also, this game will help people who want to take dancing a bit more seriously and learn some choreographies from dance videos found on the internet, improving their skills.
## 3. **Prediction**:

- ***What do we want to predict*:** My model will predict pose key points or, simply put, it will do a pose estimation. 
## 4. **Action**:

- ***What actions are linked to the prediction***: As said before, after the pose key points are estimated, the program computes the similarity scores between a pose from an uploaded choreography video and user's pose from camera feed. After the dancing video has ended, the average performance score is computed. The average performance score at the end of the dance video will motivate dedicated users to improve their skills or repeat a choreography a few times to get a better score.
## 5. **New data**:

- ***Where does new live data come from***: The model will not be trained on a new additional data. The live data comes from the camera feed as well as from a video, that users upload from their laptop to the game.
## 6. **Training data**:

- ***What data is needed to train your AI model*:** I will combine a community dataset that I have found on Kaggle (see [Mini Human Pose Dataset (kaggle.com)](https://www.kaggle.com/datasets/legosy7/mini-human-pose-dataset)) that is a mini version of famous COCO dataset with my own annotated data.
## 7. **Feedback data:**

- ***How will you test your model in the field***: I will test my model by myself, as well as engage other people (friends, classmates) to try it out.
## 8. **Value of being right**:

- ***What is the gain***: If the key points are continuously estimated correctly, the pose estimation will be accurate, providing great gaming experience for the users. 

- Additionally, if the performance scores are consistently computed without errors, the user will be able to monitor their progress or regress.  
## 9. **Cost of being wrong**:

- ***What is the impact of a bad prediction:*** It would not be a big deal if only one frame in the whole video had an incorrectly estimated pose. However, if the model consistently makes big errors, resulting in incorrect performance scores for the users, calculations of the similarity score will be incorrect too. It may cause a negative experience for users as they will receive unfairly low scores. 
## 10. **Accuracy**:

- ***What is the minimum expected performance***: I expect the accuracy to be around 90% on the test set or higher to ensure a positive gaming experience for the users. 
## 11. **Judgement**:

- ***What external info is additionally weighted to get the final conclusion**:* Robustness of the model should be weighted to the final conclusion. Since the program involves working with videos, it requires making prediction on a very high speed.

## Conclusion:

This project aims to get people moving and improve their dance skills with the usage AI to analyze poses from videos. The model uses videos and live feed from camera. Training, test and validation datasets will be composed from a combination of a Kaggle dataset and my own annotated data. Testing will be done by me and my friends and classmates.
My focus is to create a robust and fast model which handles video data well. The main purpose of me doing the project is to lighten up people's mood and fight inactivity with a fun game.