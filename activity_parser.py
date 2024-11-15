import requests
#from bs4 import BeautifulSoup
import json

class ActivityParser:
    def __init__(self, url):
        self.url = url
        self._distance = 0
        self.start_time = 0
        self.duration = 0
        self.average_speed = 0
        self.average_rate = 0
        self.name = ''
        self.start_latitude = 0
        self.start_longitude = 0
        self.parsed = False

    def _parse(self):
        pass

    def __parse_if_need(self):
        if not self.parsed:
            self._parse()
            self.parsed = True

    def get_info(self):
        self.__parse_if_need()
        return {
            'start_time': self.start_time,
            'duration': self.duration,
            'distance': self._distance,
            'average_speed': self.average_speed,
            'average_rate': self.average_rate,
            'start_latitude': self.start_latitude,
            'start_longitude': self.start_longitude,
            'name': self.name
        }

    def get_distance(self):
        self.__parse_if_need()
        return self._distance

    def get_start_time(self):
        self.__parse_if_need()
        return self.start_time

    def get_duration(self):
        self.__parse_if_need()
        return self.duration

    def get_average_speed(self):
        self.__parse_if_need()
        return self.average_speed


class GarminActivityParser(ActivityParser):

    def _parse(self):
        auth_url = 'https://connect.garmin.com/services/auth/token/public'
        auth_response = requests.post(auth_url).json()
        auth = auth_response['access_token']

        service_url = self.url.replace('modern', 'activity-service')

        headers = {
            'Authorization': 'Bearer ' + auth,
            'DI-Backend': 'connectapi.garmin.com'
        }

        response = requests.get(service_url, headers=headers)

        if response.status_code != 200:
            raise ConnectionError('Ошибка парсинга активности: ' + self.url)
            # 'https://connect.garmin.com/activity-service/activity/142311180266'

        json_response = response.json()

        self.name = json_response['activityName']
        self._distance = int(json_response['summaryDTO']['distance'])
        self.duration = int(json_response['summaryDTO']['duration'])
        self.average_speed = json_response['summaryDTO']['averageSpeed']
        self.average_rate = int(json_response['summaryDTO']['averageHR'])
        self.start_time = json_response['summaryDTO']['startTimeLocal']
        self.start_latitude = json_response['summaryDTO']['startLatitude']
        self.start_longitude = json_response['summaryDTO']['startLongitude']
        print(auth)
        print(response)


class PolarActivityParser(ActivityParser):

    def _parse(self):

        response = requests.get(self.url, headers={'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'})

        start_pos = response.text.find('trainingSessionData = {') + len(
            'trainingSessionData = ')  # .find() will return the BEGINNING of the match, so you'll need to account for the length of the string you're searching for
        end_pos = response.text.find('/*** Analyse view mode ***/') - 2

        json_chunk = response.text[start_pos:end_pos]
        json_chunk = json_chunk.strip()
        # json_chunk = json_chunk[:-1]

        json_data = json.loads(json_chunk)
        data_dictionary = json_data['curveData']
        self.name = data_dictionary['exercises'][0]['sport']['name']
        self.start_time = data_dictionary['exercises'][0]['startTime']
        self._distance = int(data_dictionary['exercises'][0]['stopDistance'] - data_dictionary['exercises'][0]['startDistance'])
        self.duration = int((data_dictionary['exercises'][0]['stopTime'] - data_dictionary['exercises'][0]['startTime']) / 1000)
        self.average_speed = data_dictionary['exercises'][0]['statistics']['SPEED']['avg']
        self.average_rate = int(data_dictionary['exercises'][0]['statistics']['HEART_RATE']['avg'])
        self.start_latitude = json_data['mapData']['samples'][0][0]['lat']
        self.start_longitude = json_data['mapData']['samples'][0][0]['lon']



class SuuntoActivityParser(ActivityParser):

    def _parse(self):
        self._distance = 'suunto'
        self.duration = 'suunto'
        self.average_speed = 'suunto'
        self.start_time = 'suunto'


def get_parser(url):
    if url.find('garmin') > 0:
        return GarminActivityParser(url)
    elif url.find('polar') > 0:
        return PolarActivityParser(url)
    elif url.find('suunto') > 0:
        return SuuntoActivityParser(url)
    else:
        return None