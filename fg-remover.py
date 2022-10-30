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
        sg.Text("Background Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 15), key="-BACKGROUND LIST-"
        )
    ],
    [
        sg.Text("Foreground Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 15), key="-FOREGROUND LIST-"
        )
    ],
]

preview_column = [
    [sg.Image(filename="", key="-IMAGE-")],
    [sg.Radio("None", "Radio", True, size=(10, 1))],
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
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        bg_image = None
        
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
                window["-BACKGROUND LIST-"].update(fnames)
                
            elif event == "-BACKGROUND LIST-":  # A file was chosen from the listbox
                try:
                    filename = os.path.join(
                        values["-FOLDER-"], values["-BACKGROUND LIST-"][0]
                    )
                    # TODO:store image in memory
                    print(filename)
                    bg_image = cv2.imread(filename)
                    bg_image = cv2.resize(bg_image, [width, height], interpolation = cv2.INTER_AREA)
                    
                
                #window["-IMAGE-"].update(filename=filename)

                except:
                    bg_image = None
                    pass
          
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

            if bg_image is None:
                bg_image = np.zeros(image.shape, dtype=np.uint8)
                bg_image[:] = BG_COLOR
                
            if values["-BLUR-"]:
                bg_image = cv2.GaussianBlur(bg_image, (21, 21), values["-BLUR SLIDER-"])
            elif values["-HUE-"]:
                bg_image = cv2.cvtColor(bg_image, cv2.COLOR_BGR2HSV)
                bg_image[:, :, 0] += int(values["-HUE SLIDER-"])
                bg_image = cv2.cvtColor(bg_image, cv2.COLOR_HSV2BGR)
            
            frame = np.where(condition, image, bg_image)
                
            imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            window["-IMAGE-"].update(data=imgbytes)
                
        window.close()
        cap.release()

main()