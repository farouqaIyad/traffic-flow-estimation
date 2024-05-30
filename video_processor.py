from db import speeding_cars_db
from collections import deque
import supervision as sv
import streamlit as st
from Cookie import *
import numpy as np
import datetime
import cv2
import os
import math


class VideoProcessor:

    def __init__(self, source_video_path, model):
        self.model = model
        self.trace_annotator = sv.TraceAnnotator(
            position=sv.Position.CENTER, trace_length=20, thickness=2
        )
        self.box_annotator = sv.BoxAnnotator(thickness=2, text_thickness=1)
        self.source_video_path = source_video_path
        self.output_video_path = r"result_videos\users\{}".format(
            os.path.basename(source_video_path)
        )
        self.classes_dict = self.model.model.names
        self.classes_names = list(self.model.model.names.values())
        self.classes_count = {}
        self.tracked_objects = list()
        self.classes_count = {i: 0 for i in self.classes_names}
        self.confidence_averages = {i: 0 for i in self.classes_names}
        self.fourcc = cv2.VideoWriter_fourcc(*"H264")
        self.writer = None

    def process(self):
        try:
            vid_cap = cv2.VideoCapture(self.source_video_path)
            while vid_cap.isOpened():
                success, image = vid_cap.read()
                if success:
                    detections = self.model.detect_and_track(image)
                    labels = list()
                    for _, _, conf, class_id, tracker_id in detections:
                        if tracker_id not in self.tracked_objects:
                            self.classes_count[self.classes_names[class_id]] += 1
                            self.tracked_objects.append(tracker_id)
                            self.confidence_averages[
                                self.classes_names[class_id]
                            ] += conf
                        labels.append(f"{self.classes_dict[class_id]} {tracker_id}")
                    frame = self.box_annotator.annotate(
                        scene=image, detections=detections, labels=labels
                    )
                    frame = self.trace_annotator.annotate(frame, detections=detections)
                    if self.writer is None:
                        self.writer = cv2.VideoWriter(
                            self.output_video_path,
                            self.fourcc,
                            vid_cap.get(cv2.CAP_PROP_FPS),
                            (frame.shape[1], frame.shape[0]),
                        )
                    self.writer.write(frame)
                else:
                    vid_cap.release()
                    break
            self.writer.release()
        except Exception as e:
            st.error("error loading video" + str(e))
        st.video(self.output_video_path)
        for i in self.classes_names:
            self.confidence_averages[i] = (
                (self.confidence_averages[i] / self.classes_count[i])
                if self.classes_count[i] != 0
                else 0
            )


class VideoAndSpeedProcessor(VideoProcessor):

    def __init__(self, source_video_path, model, speed_processor):
        super().__init__(source_video_path, model)
        self.object_postions = dict()
        self.speeding_cars = list()
        self.each_car_speed_average = dict()
        self.speed_processor = speed_processor
        self.output_video_path = (
            r"D:\AA\the jounie project\result_videos\speed_predictions\{}".format(
                os.path.basename(source_video_path)
            )
        )
        self.heatmap_path = r"D:\AA\the jounie project\charts\heat\{}.jpg".format(
            os.path.basename(source_video_path)
        )
        self.total_cars_speed_average = dict()

    def gamma_correction(self, image, gamma=1.0):
        image = image.astype(np.float32) / 255.0
        corrected = np.power(image, gamma)
        corrected = (corrected * 255).astype(np.uint8)
        return corrected

    def contrast_stretching(self, image, min_percentile=1, max_percentile=99):
        min_val, max_val = np.percentile(image, (min_percentile, max_percentile))
        stretched = np.clip(
            (image - min_val) / (max_val - min_val) * 255, 0, 255
        ).astype(np.uint8)
        return stretched

    def histogram_equalizer(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = self.gamma_correction(image, gamma=1.3)
        image = self.contrast_stretching(image)
        equal = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        return equal

    def process(self):
        for i in self.classes_names:
            self.total_cars_speed_average[i] = {}
        try:
            vid_cap = cv2.VideoCapture(self.source_video_path)
            while vid_cap.isOpened():
                success, image = vid_cap.read()
                if success:
                    detections = self.model.detect_and_track(
                        self.histogram_equalizer(image)
                    )
                    labels = list()
                    for box, _, conf, class_id, tracker_id in detections:
                        x1, y1, x2, y2 = box
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        if tracker_id not in self.object_postions:
                            self.object_postions[int(tracker_id)] = deque(maxlen=20)
                        if tracker_id not in self.tracked_objects:
                            self.tracked_objects.append(tracker_id)
                            self.each_car_speed_average[tracker_id] = deque(maxlen=30)
                            self.classes_count[self.classes_names[class_id]] += 1
                            self.confidence_averages[
                                self.classes_names[class_id]
                            ] += conf
                        self.object_postions[int(tracker_id)].append(
                            (center_x, center_y)
                        )
                        new_speed = self.speed_processor.process(
                            image,
                            box,
                            self.object_postions,
                            self.each_car_speed_average,
                            self.total_cars_speed_average,
                            tracker_id,
                            class_id,
                            self.classes_names,
                        )

                        labels.append(
                            f"{self.classes_dict[class_id]} {int(new_speed)}km/h"
                        )
                    frame = self.box_annotator.annotate(
                        scene=image, detections=detections, labels=labels
                    )
                    frame = self.trace_annotator.annotate(frame, detections=detections)
                    if self.writer is None:
                        self.writer = cv2.VideoWriter(
                            self.output_video_path,
                            self.fourcc,
                            vid_cap.get(cv2.CAP_PROP_FPS),
                            (frame.shape[1], frame.shape[0]),
                        )
                    self.writer.write(frame)
                else:
                    vid_cap.release()
                    break

            self.writer.release()
        except Exception as e:
            st.error("error loading video" + str(e))
        st.video(str(self.output_video_path))
        for i in self.classes_names:
            self.confidence_averages[i] = (
                (self.confidence_averages[i] / self.classes_count[i])
                if self.classes_count[i] != 0
                else 0
            )
        for i in self.total_cars_speed_average:
            values = list(self.total_cars_speed_average[i].values())
            self.total_cars_speed_average[i] = (
                int(sum(values) / len(values)) if len(values) != 0 else 0
            )


class SpeedProcessor:
    def __init__(self, tform=None):
        self.cookie = Cookie()
        self.scale_w = float(self.cookie.get("scale_w"))
        self.scale_h = float(self.cookie.get("scale_h"))
        self.ppm = float(self.cookie.get("ppm"))
        self.tform = tform
        self.satilite_image = cv2.imread(self.cookie.get("sat_image"))
        self.fps = self.cookie.get("fps")
        self.speeding_cars = list()

    def process(
        self,
        image,
        box,
        object_postions,
        each_car_average_speed,
        total_cars_average_speed,
        tracker_id,
        class_id,
        classes_names,
    ):
        n = len(object_postions[int(tracker_id)])

        new_speed = 0

        if n > 1:

            p1 = self.tform.inverse(
                (
                    int(object_postions[tracker_id][1][0] / 3),
                    int(object_postions[tracker_id][1][1] / 2),
                )
            )
            p2 = self.tform.inverse(
                (
                    int(object_postions[tracker_id][0][0] / 3),
                    int(object_postions[tracker_id][0][1] / 2),
                )
            )
            x1, y1 = (p1[0][0], p1[0][1])
            x2, y2 = (p2[0][0], p2[0][1])
            self.satilite_image[int(y2 - 50), int(x2)] = (0, 0, 255)
            speed = (
                math.sqrt(
                    ((x2 - x1) * self.scale_w) ** 2 + ((y2 - y1) * self.scale_h) ** 2
                )
                * self.fps
                * self.ppm
            )
            each_car_average_speed[tracker_id].appendleft(int(speed))
        if len(each_car_average_speed[tracker_id]) == 30:

            new_speed = sum(each_car_average_speed[tracker_id]) / 30
            total_cars_average_speed[classes_names[class_id]][tracker_id] = new_speed

            if (
                new_speed > 74
                and new_speed < 100
                and tracker_id not in self.speeding_cars
            ):
                x1, y1, x2, y2 = box
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

                self.speeding_cars.append(tracker_id)
                color = (255, 0, 0)
                thickness = 2
                filename = f"speeding_car_{tracker_id}.jpg"
                speeding_cars_db.insert_one(
                    {
                        "Speed": new_speed,
                        "image": filename,
                        "time": datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
                        "output_video": self.cookie.get("video"),
                    }
                )

                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
                cv2.imwrite(filename, image)
        return new_speed
