import requests
import os
import csv
from datetime import datetime
from time import sleep

from geopy.geocoders import Nominatim
from random import random

from config import DATE_FORMAT, IMAGE_FOLDER, PROF_DATA
import person_detector

geolocator = Nominatim(user_agent="auto-tinder")


class Person(object):

    def __init__(self, data, api, distance_mi=0):
        self._api = api

        self.id = data["_id"]
        self.name = data.get("name", "Unknown")

        self.bio = data.get("bio", "")
        self.distance = data.get("distance_mi", distance_mi) * 1.60934

        self.birth_date = datetime.strptime(data["birth_date"], DATE_FORMAT) if data.get(
            "birth_date", False) else None
        self.gender = ["Male", "Female", "Unknown"][data.get("gender", 2)]
        self.orientations = list(
            map(lambda orientation: orientation.get("name"), data.get("sexual_orientations", [])))

        self.images = list(map(lambda photo: photo["url"], data.get("photos", [])))

        self.jobs = list(
            map(lambda job: {"title": job.get("title", {}).get("name"),
                             "company": job.get("company", {}).get("name")}, data.get("jobs", [])))
        self.schools = list(map(lambda school: school["name"], data.get("schools", [])))

        if data.get("pos", False):
            self.location = geolocator.reverse(f'{data["pos"]["lat"]}, {data["pos"]["lon"]}')
        else:
            self.location = None

    def __repr__(self):
        return f"{self.id}  -  {self.name} ({self.birth_date.strftime('%d.%m.%Y')})"

    def like(self):
        return self._api.like(self.id)

    def dislike(self):
        return self._api.dislike(self.id)

    def download_data(self, sleep_max_for=0):
        if self.exists():
            print("Already exists, skipping.")
            return
        self.download_images(sleep_max_for)
        self.to_csv()
        print("Done.")

    def predict_likeliness(self, classifier, sess):
        ratings = []
        for image in self.images:
            req = requests.get(image, stream=True)
            tmp_filename = f"data/tmp/run.jpg"
            if req.status_code == 200:
                with open(tmp_filename, "wb") as f:
                    f.write(req.content)
            img = person_detector.get_person(tmp_filename, sess)
            if img:
                img = img.convert('L')
                img.save(tmp_filename, "jpeg")
                certainty = classifier.classify(tmp_filename)
                pos = certainty["positive"]
                ratings.append(pos)
        ratings.sort(reverse=True)
        ratings = ratings[:5]
        if len(ratings) == 0:
            return 0.001
        return ratings[0] * 0.6 + sum(ratings[1:]) / len(ratings[1:]) * 0.4

    def exists(self):
        if not os.path.exists(PROF_DATA):
            return False
        with open(PROF_DATA, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["id"] == self.id:
                    return True
        return False

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "distance": self.distance,
            "birth_date": self.birth_date.strftime(DATE_FORMAT),
            "gender": self.gender,
            "orientations": "|".join(self.orientations),
            "jobs": "|".join([f"{job['company']} <{job['title']}>" for job in self.jobs]),
            "schools": "|".join(self.schools),
            "location": self.location,
        }

    def to_csv(self):
        file_exists = os.path.exists(PROF_DATA)
        data = self.serialize()

        with open(PROF_DATA, 'a') as f:
            writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def download_images(self, sleep_max_for=0):
        index = -1
        for image_url in self.images:
            index += 1
            req = requests.get(image_url, stream=True)
            if req.status_code == 200:
                with open(f"{IMAGE_FOLDER}/{self.id}_{self.name}_{index}.jpeg", "wb") as f:
                    f.write(req.content)
            sleep(random() * sleep_max_for)


class Profile(Person):

    def __init__(self, data, api):
        super().__init__(data["user"], api)

        self.email = data["account"].get("email")
        self.phone_number = data["account"].get("account_phone_number")

        self.age_min = data["user"]["age_filter_min"]
        self.age_max = data["user"]["age_filter_max"]

        self.max_distance = data["user"]["distance_filter"]
        self.gender_filter = ["Male", "Female"][data["user"]["gender_filter"]]
