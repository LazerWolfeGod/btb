# Soundium
A project that attempts to use PyUI to its full capacity, it is a recreation of spotify.
## Requirements
It is made using pygame, and requires my module PyUI. All modules:
- pygame
- requests
- pytube
- bs4
- ffmpeg
- PyUI
In the current version of pytube in order to make it work you need to edit some code in cipher class in:
Python\Python311\Lib\site-packages\pytube\cipher.py
Go to line 272 and 273 and swap the code out for:
```py
r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)', ]
```

On my computer i have found ffmpeg to be unreliable with how it is used, my solution that fixes the problem is to take the ffmpeg.exe file in the bin folder when you install it, and place that in the same file as Soundium. And the SOundium.exe file still needs ffmpeg.exe to be in the same folder for it to runj properly, otherwise it wont download songs properly and may crash.
