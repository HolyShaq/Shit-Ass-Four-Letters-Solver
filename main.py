from PIL import Image
from ppadb.client import Client
import numpy as np
import pytesseract, time, pyautogui

with open("fourLetterWords.txt", "r") as file:
    wordList = file.read().split("\n")


def convertToString(imageFile):
    data = np.array(imageFile)  # "data" is a height x width x 4 numpy array
    red, green, blue, _ = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    others = (red != 255) & (blue != 255) & (green != 255)
    data[..., :-1][white_areas.T] = (0, 0, 0)  # Transpose back needed
    data[..., :-1][others.T] = (255, 255, 255)

    im2 = Image.fromarray(data)

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(im2, config="--psm 10 letters")

    if text == "":
        text = "I"

    print(text, " recognized")
    return text


def findWord(posDict):
    global prevWord
    print("")

    while True:
        letters = []

        for key in posDict:
            letters.append(posDict[key].lower())

        for word in wordList:
            done = True
            for letter in letters:
                if "".join([c for c in letters]).count(letter) != word.count(letter):
                    done = False
                    break
            if done:
                break

        if word == prevWord:
            wordList.remove(word)

            with open("fourLetterWords.txt", "w") as file:
                text = ""
                for w in wordList:
                    text += w+"\n"
                file.write(text)
        else:
            break

    curWord = word
    prevWord = curWord

    inversePosDict = [(posDict[key], key) for key in posDict]
    steps = []

    for letter in curWord:
        for key, val in inversePosDict[:]:
            if letter == key.lower():
                steps.append(val)
                inversePosDict.remove((key, val))

    if not steps or curWord == wordList[-1]:
        for key in posDict:
            if posDict[key] == "C":
                posDict.update({key: "O"})
                return posDict
            if posDict[key] == "O":
                posDict.update({key: "C"})
                return posDict
            if posDict[key] == "D":
                posDict.update({key: "P"})
                return posDict
            if posDict[key] == "P":
                posDict.update({key: "D"})
            if posDict[key] == "LJ" or posDict[key] == "LY":
                posDict.update({key: "P"})
                return posDict

    print(curWord.upper(), " is the solution!")
    return steps


client = Client()
device = client.devices()[0]

device.shell("input tap 532 2185")
time.sleep(.45)

prevWord = ""
while True:
    print("\nParsing screen")
    screenshot = device.screencap()
    with open("screenshot.png", "wb") as img:
        img.write(screenshot)
    screenImage = Image.open("screenshot.png")

    btnTop = (415, 1064, 658, 1328)
    btnRight = (641, 1293, 883, 1556)
    btnBottom = (420, 1511, 673, 1779)
    btnLeft = (189, 1290, 437, 1553)

    btnTopImg = screenImage.crop(btnTop)
    btnRightImg = screenImage.crop(btnRight)
    btnBottomImg = screenImage.crop(btnBottom)
    btnLeftImg = screenImage.crop(btnLeft)

    letters = {
        "top": convertToString(btnTopImg),
        "right": convertToString(btnRightImg),
        "bottom": convertToString(btnBottomImg),
        "left": convertToString(btnLeftImg)
    }

    commands = {
        "top": "input tap 532 1209",
        "right": "input tap 764 1427",
        "bottom": "input tap 530 1630",
        "left": "input tap 314 1409"
    }

    pyAGCommands = {
        "top": (232, 546),
        "right": (325, 634),
        "bottom": (228, 731),
        "left": (140, 640)
    }

    steps = findWord(letters)
    while type(steps) == dict:
        print("New: ", steps)
        steps = findWord(steps)

    for step in steps:
        print(step)
        #  ADB Shell
        # device.shell(commands[step])

        # PyAutoGui
        x, y = pyAGCommands[step]
        pyautogui.click(x=x, y=y)
