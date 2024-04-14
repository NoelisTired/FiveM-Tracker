import pyautogui
import keyboard
import requests
import io
import base64
import threading
import time
import os
import json
import re

class ScreenTextDetector:
    def __init__(self) -> None:
        self.last_event_time = 0
        self.rate_limit = 3
        self.screen_width, self.screen_height = pyautogui.size()
        self.middle_x, self.middle_y = int(self.screen_width/2), int(self.screen_height/2)
        

    """
        This function is responsible for taking a screenshot of the game and sending it to the Google Vision API for OCR. (with free apikey lol)
    """
    def take_screenshot(self) -> tuple:
        os.system('cls')
        print("[OCR] Taking Screenshot")
        screenshot = pyautogui.screenshot(region=(self.middle_x-400, self.middle_y-300, 800, 600))
        # Convert the screenshot to bytes
        with io.BytesIO() as output:
            screenshot.save(output, format="PNG")
            screenshot.save('screenshot.png')
            print("[OCR] Successfully saved Screenshot")
            screenshot_bytes = output.getvalue()
        base64string = base64.b64encode(screenshot_bytes).decode()
        headers = {
            'x-origin': 'https://explorer.apis.google.com',
            'Content-Type': 'application/json'
        }
        params = {
            'alt': 'json',
            'key': 'AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM',
        }
        json_data = {
            "requests": [
                {
                    "image": {
                        "content": base64string
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION"
                        }
                    ]
                }
            ]
        }
        
        try:
            print("[OCR] - Submitting to API")
            response = requests.post('https://content-vision.googleapis.com/v1/images:annotate', params=params, headers=headers, json=json_data, timeout=10)
            response_data = response.json()
            if response.json() == {'responses': [{}]}:
                return "No useful information found"
            text_annotations = response_data['responses'][0]['textAnnotations']
            detected_numbers = []
            for annotation in text_annotations:
                try:
                    if re.match('^[0-9]*$',annotation['description']):
                        number = int(annotation['description'])
                        is_duplicate = any(number == t for t in detected_numbers)
                        if number != 0 and number < 10000:
                            if not is_duplicate:
                                detected_numbers.append(number)
                except ValueError:
                    pass
            if len(detected_numbers) > 0:
                print(f"Detected {len(detected_numbers)} players")
                return detected_numbers
            else:
                return "No integer values found.."
        except requests.Timeout:
            return "API exceeded 10000ms.."
