import os
from pathlib import Path

import tensorflow.compat.v1 as tf

from config import IMAGE_FOLDER, POS_FOLDER, NEG_FOLDER
import person_detector

command = """
python retrain.py --bottleneck_dir=tf/training_data/bottlenecks --model_dir=tf/training_data/inception --summaries_dir=tf/training_data/summaries/basic --output_graph=tf/training_output/retrained_graph.pb --output_labels=tf/training_output/retrained_labels.txt --image_dir=./data/classified --how_many_training_steps=50000 --testing_percentage=20 --learning_rate=0.001
"""


def filter_images(images, prefix):
    classified = [str(path).split('/')[-1].replace('jpg', 'jpeg') for path in
                  Path("./data/classified").rglob('*.jpg')]
    skipped = [str(path).split('/')[-1].replace('jpg', 'jpeg') for path in
               Path("./data/skipped").rglob('*.jpg')]
    handled = set(classified)
    handled.update(skipped)
    unclassified = set(filter(lambda image: (image.startswith(prefix)), images))
    return sorted(unclassified - handled)


def move_images(images, folder, label):
    for i, image in enumerate(images):
        old_filename = IMAGE_FOLDER + "/" + image
        new_filename = folder + "/" + image[:-5] + ".jpg"
        skip_filename = f'./data/skipped/{label}/{image[:-5]}.jpg'

        print(f'{i + 1}/{len(images)}\tMoving {label}: {image}...', end=' ')
        person_found, person_img = person_detector.get_person(old_filename, sess)
        if not person_found:
            if person_img:
                person_img = person_img.convert('L')
                person_img.save(skip_filename, "jpeg")
                print('Skipping.')
            else:
                print('Skipping, no person.')
            continue
        person_img = person_img.convert('L')
        person_img.save(new_filename, "jpeg")
        print('Done.')


if __name__ == "__main__":
    detection_graph = person_detector.open_graph()

    images = [f for f in os.listdir(IMAGE_FOLDER) if os.path.isfile(os.path.join(IMAGE_FOLDER, f))]
    positive_images = filter_images(images, '1_')
    negative_images = filter_images(images, '0_')

    with detection_graph.as_default():
        with tf.Session() as sess:
            move_images(positive_images, POS_FOLDER, 'positive')
            move_images(negative_images, NEG_FOLDER, 'negative')
