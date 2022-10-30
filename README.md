# Foreground Remover

- [Foreground Remover](#foreground-remover)
  - [Overview](#overview)
    - [Referenced Code](#referenced-code)
    - [Installation](#installation)
    - [Usage](#usage)

## Overview

This is an implementation of Mediapipe that reverses the background mask to make it a foreground mask. There is some implementation with pygui to provide foreground image selection and masking properties.

This project was created as a halloween virtual costume, to make someone appear as a ghost in a Teams/Zoom type meeting.

### Referenced Code

This project borrows heavily from the following code snippets:

- https://google.github.io/mediapipe/solutions/selfie_segmentation.html
- https://realpython.com/pysimplegui-python/

### Installation

```BASH
git clone https://github.com/patrickslarson8/foreground-remover
pip3 install -r requirements.txt
```

### Usage

```BASH
python3 fg-remover.py
```
