import os
import math
from random import uniform
import PySimpleGUI as sg
from PIL import Image
import cv2
import numpy as np
import pyvirtualcam
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation

BG_COLOR = (192, 192, 192)

## Layout columns
file_list_column = [
    [
        sg.Text("Background Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-BG FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 15), key="-BACKGROUND LIST-"
        )
    ],
    [
        sg.Text("Foreground Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FG FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 15), key="-FOREGROUND LIST-"
        )
    ],
        #[sg.Radio("None", "Radio", True, size=(10, 1))],
    [
        #sg.Radio("blur", "Radio", size=(10, 1), key="-BLUR-"),
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
        #sg.Radio("hue", "Radio", size=(10, 1), key="-HUE-"),
        sg.Slider(
            (0, 225),
            0,
            1,
            orientation="h",
            size=(40, 15),
            key="-HUE SLIDER-",
        ),
    ],
    [
        #sg.Radio("transparency", "Radio", size=(10, 1), key="-TRANSPARENCY-"),
        sg.Slider(
            (0, 100),
            100,
            1,
            orientation="h",
            size=(40, 15),
            key="-TRANSPARENCY SLIDER-",
        ),
    ],
    [
        #sg.Radio("threshold", "Radio", size=(10, 1), key="-THRESHOLD-"),
        sg.Slider(
            (0, 100),
            0,
            1,
            orientation="h",
            size=(40, 15),
            key="-THRESHOLD SLIDER-",
        ),
    ],
    [sg.Button("Exit", size=(10, 1))],
    [sg.Button("Ghostly", size=(10, 1))],
]

preview_column = [
    [sg.Image(filename="", key="-IMAGE-")],
]

def main():
    bg_image = None
    fg_image = None
    is_bg_remove = True
    ghost_cycle = False
    threshold = 0.1
    amt_opaque = 1
    amt_transparent = 0
    
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
    
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        
        with pyvirtualcam.Camera(width=width, height=height, fps=20) as cam:
        
            while True:
                event, values = window.read(timeout=20)
                if event == "Exit" or event == sg.WIN_CLOSED:
                    break
                
                elif event == "Ghostly":
                    ghost_cycle = not ghost_cycle
                elif event == "-BG FOLDER-":
                    folder = values["-BG FOLDER-"]
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
                    
                elif event == "-FG FOLDER-":
                    folder = values["-FG FOLDER-"]
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
                    window["-FOREGROUND LIST-"].update(fnames)
                    
                elif event == "-BACKGROUND LIST-":  # A file was chosen from the listbox
                    is_bg_remove = True
                    try:
                        filename = os.path.join(
                            values["-BG FOLDER-"], values["-BACKGROUND LIST-"][0]
                        )
                        bg_image = cv2.imread(filename)
                        bg_image = cv2.resize(bg_image, [width, height], interpolation = cv2.INTER_AREA)
                    except:
                        bg_image = None
                        pass
                
                elif event == "-FOREGROUND LIST-":  # A file was chosen from the listbox
                    is_bg_remove = False
                    try:
                        filename = os.path.join(
                            values["-FG FOLDER-"], values["-FOREGROUND LIST-"][0]
                        )
                        fg_image = cv2.imread(filename)
                        fg_image = cv2.resize(fg_image, [width, height], interpolation = cv2.INTER_AREA)
                    except:
                        fg_image = None
                        pass
            
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
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
                if is_bg_remove:
                    condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > threshold
                    mat = bg_image
                else:
                    condition = np.stack((results.segmentation_mask,) * 3, axis=-1) < threshold
                    mat = fg_image

                # Apply effects
                
                if mat is None:
                    mat = np.zeros(image.shape, dtype=np.uint8)
                    mat[:] = BG_COLOR
                    
                mat = cv2.GaussianBlur(mat, (21, 21), values["-BLUR SLIDER-"])
                mat = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV)
                mat[:, :, 0] += int(values["-HUE SLIDER-"])
                mat = cv2.cvtColor(mat, cv2.COLOR_HSV2BGR)
                
                if (not ghost_cycle):
                    amt_transparent = float(values["-TRANSPARENCY SLIDER-"]/100)
                else:
                    if amt_transparent < 0.05:
                        amt_transparent += 0.05
                    elif amt_transparent > 0.5:
                        amt_transparent -= 0.05
                    else:
                        amt_transparent += uniform(-0.05, 0.05)
                            
                amt_opaque = 1 - amt_transparent
                threshold = float(values["-THRESHOLD SLIDER-"]/100)
                
                # Process the transparency effect
                mat_additive = mat * amt_opaque
                image = image * amt_transparent
                image = image + mat_additive
                image = image.astype(np.uint8)
                    
                
                frame = np.where(condition, image, mat)
                
                # Update virtual cam
                cam.send(frame)
                cam.sleep_until_next_frame()
                
                # Update preview
                imgbytes = cv2.imencode(".png", frame)[1].tobytes()
                window["-IMAGE-"].update(data=imgbytes)
                
        window.close()
        cap.release()

main()