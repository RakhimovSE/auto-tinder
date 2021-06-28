from time import sleep

from random import random

from config import TOKEN
from tinder_api import TinderAPI

if __name__ == "__main__":
    api = TinderAPI(TOKEN)

    counter = 0
    while True:
        persons = api.nearby_persons()
        for person in persons:
            counter += 1
            print(f'{counter}. {person.name}...', end=' ')
            person.download_data(sleep_max_for=random() * 3)
            sleep(random() * 10)
        sleep(random() * 10)
