#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import cv2
import numpy as np
import pyautogui
import threading
from queue import Queue
import time

# Function to capture screen and write frames to video
def screen_record(queue):
    # Screen resolution
    SCREEN_SIZE = (1920, 1080)
    # Video codec and output format for MP4
    codec = cv2.VideoWriter_fourcc(*"mp4v")
    output = cv2.VideoWriter("screen_recording.mp4", codec, 20.0, SCREEN_SIZE)

    while not exit_flag:
        # Capture screen image
        img = pyautogui.screenshot()
        # Convert the image to a numpy array
        frame = np.array(img)
        # Convert the image from BGR color (which OpenCV uses) to RGB color
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Write the frame to the output video file
        output.write(frame)
        # Put frame in the queue for object detection
        queue.put(frame)
        # Display the frame in the screen recording window
        cv2.imshow("Screen Recording", frame)
        cv2.waitKey(1)
        time.sleep(0.05)  # Adjust the delay as needed

    # Release the video writer
    output.release()

# Function to perform object detection
def object_detection(queue):
    from roboflow import Roboflow
    import cv2 as cv

    rf = Roboflow(api_key="mBpJmBoaKiCx1RiriSWy")
    project = rf.workspace().project("pistol-wgcvl")
    roboflow_model = project.version(1).model

    highest_confidence_frame = None
    highest_confidence_score = 0.0

    while not exit_flag:
        if not queue.empty():
            frame = queue.get()
            # save frame as a temporary jpeg file
            cv.imwrite('temp.jpg', frame)
            # run inference on temporary jpeg file (the frame)
            predictions = roboflow_model.predict('temp.jpg')
            predictions_json = predictions.json()
            # printing all detection results from the image
            print(predictions_json)

            # Find the bounding box with the highest confidence score
            for bounding_box in predictions:
                confidence_score = bounding_box['confidence']
                if confidence_score > highest_confidence_score:
                    highest_confidence_score = confidence_score
                    highest_confidence_frame = frame.copy()

            # Display the frame with the highest confidence score
            if highest_confidence_frame is not None:
                cv.imshow("Highest Confidence Frame", highest_confidence_frame)
                cv.waitKey(1)

    cv.destroyAllWindows()

# Flag to indicate when to stop
exit_flag = False

# Create a queue for passing frames between threads
frame_queue = Queue()

# Start the screen recording thread
screen_thread = threading.Thread(target=screen_record, args=(frame_queue,))
screen_thread.start()

# Start the object detection thread
object_detection_thread = threading.Thread(target=object_detection, args=(frame_queue,))
object_detection_thread.start()

# Wait for the user to press 'q' to stop the recording
while True:
    if cv2.waitKey(1) == ord("q"):
        exit_flag = True
        break

# Wait for threads to finish
screen_thread.join()
object_detection_thread.join()

# Close OpenCV windows
cv2.destroyAllWindows()


# In[ ]:




