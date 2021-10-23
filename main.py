# @uthor - Monty Gupta
# montygupta9759538717@gmail.com

import requests
import json
import pyttsx3 #text to speech
import speech_recognition as sr #to recognise speech
import re #reg x (check if a string contains the specified search pattern)
import threading
import time

API_KEY = "toTCYyx7og1w"
PROJECT_TOKEN = "tFJCuVH2GqJA"
RUN_TOKEN = "tU5E2ZnzsvXL"


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        #fetching data
        response = requests.get(f'https://parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params= self.params)
        data = json.loads(response.text) # doing this so that can update the data at any point i.e giving recent run
        return data

    def get_total_cases(self):
        data = self.data['Total']

        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']

    def get_total_deaths(self):
        data = self.data['Total']

        for content in data:
            if content['name'] == "Deaths:":
                return content['value']            
        return "0"

    def get_country_data(self, country):
        data = self.data['Country']
        
        for content in data:
            if content['name'].lower() == country.lower():
                return content
        return "0"

    def get_list_of_countries(self):
        Countries = []

        for country in self.data['Country']:
            Countries.append(country['name'].lower())

        return Countries

    # used threading
    def update_info(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params) # this endpoint return most recent data
        

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()

                if new_data != old_data:
                    self.data = new_data
                    print("Data Updated")
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()

# voice assistant work

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    rev = sr.Recognizer()
    with sr.Microphone() as source:
        audio = rev.listen(source)
        said = ""

        try:
            said = rev.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()

def main():
    print("Here We Begin!!!")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop"
    country_list = data.get_list_of_countries()
    

    TOTAL_PATTERNS = {

        # these regx works like if our sentence contains total ans many words before that ans many after that it will return the result for total 

        re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths
    }

    COUNTRY_PATTERNS = {

		re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['Total_cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['Total_deaths'],
	}

    UPDATE_COMMAND = "update"


    while True:
        print("Listening..., Ask me!!")
        text = get_audio()
        print(text)
        result = None
        
        
        for pattern , func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                # check in country list
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break


        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break

        if text == UPDATE_COMMAND:
            result = "Data is being updated. This will take a moment!"
            data.update_info()

        if result:
                speak(result)

        if text.find(END_PHRASE) != -1: #stop loop
            print("Exit")
            break

main()