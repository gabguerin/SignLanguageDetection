import cv2
import os
import numpy as np
import pickle as pkl
import mediapipe as mp
from mediapipe_utils import mediapipe_detection


def landmark_to_array(landmark_list):
    keypoints = []
    for landmark in landmark_list.landmark:
        keypoints.append([landmark.x, landmark.y, landmark.z])
    return np.array(keypoints)


def extract_keypoints(results):
    """ Extract the results of both hands and convert them to a np array of size
    if a hand doesn't appear, return an array of zeros

    :param results: mediapipe object that contains the 3D position of all keypoints
    :return: Two np arrays of size (1, 21 * 3) = (nb_keypoints * nb_coordinates) corresponding to both hands
    """
    pose = landmark_to_array(results.pose_landmarks).reshape(63).tolist()

    left_hand = np.zeros(63).tolist()
    if results.left_hand_landmarks:
        left_hand = landmark_to_array(results.left_hand_landmarks).reshape(63).tolist()

    right_hand = np.zeros(63).tolist()
    if results.right_hand_landmarks:
        right_hand = landmark_to_array(results.right_hand_landmarks).reshape(63).tolist()
    return pose, left_hand, right_hand


def save_landmarks_from_video(video, folder="videos"):
    landmark_list = {"pose": [], "left_hand": [], "right_hand": []}
    sign_name = video.replace(".mp4", "")

    # Set the Video stream
    cap = cv2.VideoCapture(os.path.join(folder, video))
    with mp.solutions.holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Make detections
                image, results = mediapipe_detection(frame, holistic)

                # Store results
                pose, left_hand, right_hand = extract_keypoints(results)
                landmark_list["pose"].append(pose)
                landmark_list["left_hand"].append(left_hand)
                landmark_list["right_hand"].append(right_hand)
            else:
                break
        cap.release()

    # Create the folder if not exists
    path = os.path.join("data/dataset", sign_name)
    if not os.path.exists(path):
        os.mkdir(path)

    # Saving the landmark_list in the correct folder
    save_array(landmark_list["pose"], os.path.join(path, f"pose_{sign_name}.pickle"))
    save_array(landmark_list["left_hand"], os.path.join(path, f"lh_{sign_name}.pickle"))
    save_array(landmark_list["right_hand"], os.path.join(path, f"rh_{sign_name}.pickle"))


def save_array(arr, path):
    file = open(path, "wb")
    pkl.dump(arr, file)
    file.close()


def load_array(path):
    file = open(path, "rb")
    arr = pkl.load(file)
    file.close()
    return np.array(arr)