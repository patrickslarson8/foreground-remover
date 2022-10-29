import os
import PySimpleGUI as sg
from PIL import Image
import cv2
import numpy as np


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

# # Run the Event Loop
# while True:
#     event, values = window.read()
#     if event == "Exit" or event == sg.WIN_CLOSED:
#         break
#     # Folder name was filled in, make a list of files in the folder
#     if event == "-FOLDER-":
#         folder = values["-FOLDER-"]
#         try:
#             # Get list of files in folder
#             file_list = os.listdir(folder)
#         except:
#             file_list = []

#         fnames = [
#             f
#             for f in file_list
#             if os.path.isfile(os.path.join(folder, f))
#             and f.lower().endswith((".png", ".gif"))
#         ]
#         window["-FILE LIST-"].update(fnames)
#     elif event == "-FILE LIST-":  # A file was chosen from the listbox
#         try:
#             filename = os.path.join(
#                 values["-FOLDER-"], values["-FILE LIST-"][0]
#             )
#             window["-TOUT-"].update(filename)
            
#             with Image.Open(filename) as im:
#                 im.show()
            
#             #window["-IMAGE-"].update(filename=filename)

#         except:
#             pass


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

    window.close()

main()