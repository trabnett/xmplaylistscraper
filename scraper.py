import requests
import csv
import os
import datetime
from dateutil.relativedelta import relativedelta

# 'https://xmplaylist.com/api/search?artistName=Howie+Mandel&trackName=43+Years&timeAgo=5184000'

from albums import album_data
import json

class XMPlaylistScraper():

    def __init__(self, *args, refresh_token, **kwargs):
        self.refresh_token = refresh_token

    def scrape(self):
        try:
            number, time_stamp, prev_json = self.get_file_number_last_date_and_last_file()
            last_datetime = datetime.datetime.fromtimestamp(time_stamp)
            now = datetime.datetime.now()
            total_seconds = None

            if number == 0:
                print('This is your first time runnning this scraper.\n'
                    'Outputs can be found in the files folder.')
                total_seconds = 5184000
                add_comparison= False

            else:
                run_since_last_file = input(
                    f'Hi Sharla!\n'
                    f'You last ran this process on {last_datetime.date().isoformat()} around {self.hour_as_am_or_pm(last_datetime.hour)}. \n'
                    f'Would you like to continue where you left off?(y/n):\n')
                while total_seconds == None:
                    if not run_since_last_file:
                        run_since_last_file = input(
                            f'You last ran this process on {last_datetime.date().isoformat()} around {self.hour_as_am_or_pm(last_datetime.hour)}. \n'
                            f'Would you like to continue where you left off?(y/n):\n')
                    elif  run_since_last_file.lower() not in ['y', 'n']:
                        run_since_last_file = input('Please enter "y" or "n":\n')
                    elif run_since_last_file.lower() == 'n':
                        print(
                            'Okay. The file we output will not contain comparisons to any previous file.\n'
                            'It will just represent the time period you specify.')
                        n_days = input('How many days ago would you like to start collecting results:\n')
                        while not n_days.isdigit():
                            n_days = input('Please enter a valid number:\n')
                        total_seconds = int((now - (now - relativedelta(days=int(n_days)))).total_seconds())
                        add_comparison = False
                    elif run_since_last_file.lower() == 'y':
                        total_seconds = int((now - last_datetime).total_seconds())
                        add_comparison = True


            file_name = f'files/{number + 1}*{now.date().isoformat()}*{int(now.timestamp())}.csv'
            known_channels_file = open('known_channels.json')
            known_channels = json.loads(known_channels_file.read()).get('known_channels')

            result = []

            access_token = self.get_auth_token()

            headers = {'Authorization': f'Bearer {access_token}'}

            for i in album_data:
                res = requests.get(f'https://xmplaylist.com/api/search?artistName={i.get("artist")}&trackName={i.get("track")}&timeAgo={total_seconds}', headers=headers)
                data = res.json()
                if data.get('stationsCounts'):
                    for sc in data.get('stationsCounts'):
                        station_name = sc.get('name')
                        if sc.get('name') not in known_channels:
                            known_channels.append(sc.get('name'))
                        if add_comparison:
                            difference_name = sc.get('name') + '_Difference'
                            if difference_name not in known_channels:
                                known_channels.append(difference_name)
                        i[sc.get('name')] = sc.get('value')
                        if add_comparison:
                            prev_record = [j for j in prev_json if j.get('track') == i.get('track')]
                            if len(prev_record) == 1:
                                prev_record = prev_record[0]
                                keys = self.get_keys(prev_record)
                                for k in keys:
                                    i[k + '_Difference'] = self.get_period_difference(i.get(k), prev_record.get(k))

                result.append(i)

            titles = ['artist', 'track'] + known_channels
            with open(file_name, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=titles)
                writer.writeheader()
                for r in result:
                    row_data = {
                        'artist': r.get('artist'), 
                        'track': r.get('track')
                    }
                    for channel in known_channels:
                        row_data[channel] = r.get(channel) or 0
                    writer.writerow(row_data)


            with open('known_channels.json', 'w') as f:
                json.dump({'known_channels': known_channels}, f)
            return True
        except Exception as e:
            raise Exception(f'An error has occurred: {e}')

    def csv_to_json(self, file_path):
        res = []
        with open(file_path, 'r') as f:
            csvFile = csv.DictReader(f)
            for line in csvFile:
                res.append(line)
        return res

    def hour_as_am_or_pm(self, hour):
        if hour < 12:
            return f'{hour}AM'
        else:
            return f'{hour - 12}PM'

    def get_file_number_last_date_and_last_file(self):
        files = [i for i in os.listdir('files') if i[:1] != '.']
        if not len(files):
            return 0, int((datetime.datetime.now() - relativedelta(seconds=5184000)).timestamp()), {}
        files.sort(reverse=True)
        last_file = files[0]
        split_last_file = last_file.split('*')
        number = int(split_last_file[0])
        time_stamp = int(split_last_file[2].split('.')[0]) if len(split_last_file) == 3 else None
        return number, time_stamp, self.csv_to_json(f'files/{last_file}')

    def get_keys(self, dict):
        keys = [i for i in dict.keys() if i not in ['artist', 'track',] and '_Difference' not in i]
        return keys

    def get_period_difference(self, current, previous):
        current_count = int(current) if type(current) == int or (type(current) ==  str and current.isdigit()) else 0
        previous_count = int(previous) if type(previous) == int or (type(previous) ==  str and previous.isdigit()) else 0
        return current_count - previous_count

    def get_auth_token(self):
        auth_url = 'https://securetoken.googleapis.com/v1/token?key=AIzaSyBSf-hIPK5-ev9ggIpzGiBWQUawsucGR9E'

        payload = {'refresh_token': self.refresh_token, 'grant_type': 'refresh_token'}

        res = requests.post(auth_url, data=payload, headers={'referer': 'https://xmplaylist.com'} )

        return res.json().get('access_token')