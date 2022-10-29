import os
import PySimpleGUI as sg
from PIL import Image
import cv2
import numpy as np
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation

BG_COLOR = (192, 192, 192)

## Layout columns
file_list_column = [
    [
        sg.Text("Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]

preview_column = [
    [sg.Text("Foreground Remover", size=(60, 1), justification="center")],
    [sg.Image(filename="", key="-IMAGE-")],
    [sg.Radio("None", "Radio", True, size=(10, 1))],
    [
        sg.Radio("threshold", "Radio", size=(10, 1), key="-THRESH-"),
        sg.Slider(
            (0, 255),
            128,
            1,
            orientation="h",
            size=(40, 15),
            key="-THRESH SLIDER-",
        ),
    ],

    [
        sg.Radio("blur", "Radio", size=(10, 1), key="-BLUR-"),
        sg.Slider(
            (1, 11),
            1,
            1,
            orientation="h",
            size=(40, 15),
            key="-BLUR SLIDER-",
        ),
    ],
    [
        sg.Radio("hue", "Radio", size=(10, 1), key="-HUE-"),
        sg.Slider(
            (0, 225),
            0,
            1,
            orientation="h",
            size=(40, 15),
            key="-HUE SLIDER-",
        ),
    ],
    [sg.Button("Exit", size=(10, 1))],
]

# cap = cv2.VideoCapture(0)

# with mp_selfie_segmentation.SelfieSegmentation(
#     model_selection=1) as selfie_segmentation:
#   bg_image = None
#   while cap.isOpened():
#     success, image = cap.read()
#     if not success:
#       print("Ignoring empty camera frame.")
#       # If loading a video, use 'break' instead of 'continue'.
#       continue

#     # Flip the image horizontally for a later selfie-view display, and convert
#     # the BGR image to RGB.
#     image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
#     # To improve performance, optionally mark the image as not writeable to
#     # pass by reference.
#     image.flags.writeable = False
#     results = selfie_segmentation.process(image)

#     image.flags.writeable = True
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#     # Draw selfie segmentation on the background image.
#     # To improve segmentation around boundaries, consider applying a joint
#     # bilateral filter to "results.segmentation_mask" with "image".
#     condition = np.stack(
#       (results.segmentation_mask,) * 3, axis=-1) > 0.1
#     # The background can be customized.
#     #   a) Load an image (with the same width and height of the input image) to
#     #      be the background, e.g., bg_image = cv2.imread('/path/to/image/file')
#     #   b) Blur the input image by applying image filtering, e.g.,
#     #      bg_image = cv2.GaussianBlur(image,(55,55),0)
#     if bg_image is None:
#       bg_image = np.zeros(image.shape, dtype=np.uint8)
#       bg_image[:] = BG_COLOR
#     output_image = np.where(condition, image, bg_image)

#     cv2.imshow('MediaPipe Selfie Segmentation', output_image)
#     if cv2.waitKey(5) & 0xFF == 27:
#       break
# cap.release()

def main():
    sg.theme("LightGreen")
    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(preview_column),
        ]
    ]

    # Create the window and show it without the plot
    window = sg.Window("Foreground Remover", layout, location=(800, 400))
    with mp_selfie_segmentation.SelfieSegmentation(
     model_selection=1) as selfie_segmentation:
        cap = cv2.VideoCapture(0)
        while True:
            event, values = window.read(timeout=20)
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            
            elif event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    # Get list of files in folder
                    file_list = os.listdir(folder)
                except:
                    file_list = []

                fnames = [
                    f
                    for f in file_list
                    if os.path.isfile(os.path.join(folder, f))
                    and f.lower().endswith((".png", ".gif"))
                ]
                window["-FILE LIST-"].update(fnames)
            elif event == "-FILE LIST-":  # A file was chosen from the listbox
                try:
                    filename = os.path.join(
                        values["-FOLDER-"], values["-FILE LIST-"][0]
                    )
                    # TODO:store image in memory
                    print(filename)
                
                #window["-IMAGE-"].update(filename=filename)

                except:
                    pass

            ret, frame = cap.read()

            if values["-THRESH-"]:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)[:, :, 0]
                frame = cv2.threshold(
                    frame, values["-THRESH SLIDER-"], 255, cv2.THRESH_BINARY
                )[1]
            elif values["-BLUR-"]:
                frame = cv2.GaussianBlur(frame, (21, 21), values["-BLUR SLIDER-"])
            elif values["-HUE-"]:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                frame[:, :, 0] += int(values["-HUE SLIDER-"])
                frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)


            imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            window["-IMAGE-"].update(data=imgbytes)
            
            bg_image = None
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            results = selfie_segmentation.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw selfie segmentation on the background image.
            # To improve segmentation around boundaries, consider applying a joint
            # bilateral filter to "results.segmentation_mask" with "image".
            condition = np.stack(
            (results.segmentation_mask,) * 3, axis=-1) > 0.1
            # The background can be customized.
            #   a) Load an image (with the same width and height of the input image) to
            #      be the background, e.g., bg_image = cv2.imread('/path/to/image/file')
            #   b) Blur the input image by applying image filtering, e.g.,
            #      bg_image = cv2.GaussianBlur(image,(55,55),0)
            if bg_image is None:
                bg_image = np.zeros(image.shape, dtype=np.uint8)
                bg_image[:] = BG_COLOR
                output_image = np.where(condition, image, bg_image)

                cv2.imshow('MediaPipe Selfie Segmentation', output_image)

        window.close()
        cap.release()

main()