from traffic_flow_est.DetectionsManage import DetectionsManager
from functions import get_cookie
from typing import List, Tuple
from ultralytics import YOLO
import supervision as sv
import streamlit as st
from Cookie import *
import numpy as np
import torch
import cv2
import os

COLORS = sv.ColorPalette.default()
device = "cuda" if torch.cuda.is_available() else "cpu"


def initiate_polygon_zones(
    polygons: List[np.ndarray],
    frame_resolution_wh: Tuple[int, int],
    triggering_position: sv.Position = sv.Position.CENTER,
) -> List[sv.PolygonZone]:
    return [
        sv.PolygonZone(
            polygon=polygon,
            frame_resolution_wh=frame_resolution_wh,
            triggering_position=triggering_position,
        )
        for polygon in polygons
    ]


cookie = Cookie()


def app():
    get_cookie(cookie, "zones_in")
    get_cookie(cookie, "zones_out")
    processor = VideoProcessor(
        source_weights_path=r"C:\Users\NITRO 5\Desktop\All_JUP\visDrone\best (2).pt",
        source_video_path=r"C:\Users\NITRO 5\Desktop\All_JUP\videos\traffic_analysis.mov",
        target_video_path=r"C:\Users\NITRO 5\Desktop\All_JUP\videos\hawdi.mov",
        confidence_threshold=0.3,
        iou_threshold=0.7,
    )
    processor.process_video()
    st.video(r"D:\AA\the jounie project\result_videos\traffic_analysis.mov")


class VideoProcessor:
    def __init__(
        self,
        source_weights_path: str,
        source_video_path: str,
        target_video_path: str = None,
        confidence_threshold: float = 0.3,
        iou_threshold: float = 0.7,
    ) -> None:
        self.conf_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.source_video_path = source_video_path
        self.target_video_path = target_video_path

        self.model = YOLO(source_weights_path).to(device)
        self.tracker = sv.ByteTrack()

        self.video_info = sv.VideoInfo.from_video_path(source_video_path)
        self.zones_in = initiate_polygon_zones(
            get_cookie(cookie, "zones_in"),
            self.video_info.resolution_wh,
            sv.Position.CENTER,
        )
        self.zones_out = initiate_polygon_zones(
            get_cookie(cookie, "zones_out"),
            self.video_info.resolution_wh,
            sv.Position.CENTER,
        )

        self.box_annotator = sv.BoxAnnotator(color=COLORS)
        self.trace_annotator = sv.TraceAnnotator(
            color=COLORS, position=sv.Position.CENTER, trace_length=100, thickness=2
        )
        self.detections_manager = DetectionsManager()

    def process_video(self):
        if self.target_video_path:
            vid_cap = cv2.VideoCapture(self.source_video_path)
            writer = None
            while vid_cap.isOpened():
                success, image = vid_cap.read()
                if success:
                    annotated_frame = self.process_frame(image)
                    if writer is None:
                        output = r"result_videos\{}".format(
                            os.path.basename(self.source_video_path)
                        )
                        fourcc = cv2.VideoWriter_fourcc(*"H264")
                        writer = cv2.VideoWriter(
                            output,
                            fourcc,
                            vid_cap.get(cv2.CAP_PROP_FPS),
                            (annotated_frame.shape[1], annotated_frame.shape[0]),
                        )
                    writer.write(annotated_frame)
                else:
                    vid_cap.release()
                    break
            writer.release()

    def annotate_frame(
        self, frame: np.ndarray, detections: sv.Detections
    ) -> np.ndarray:
        annotated_frame = frame.copy()
        for i, (zone_in, zone_out) in enumerate(zip(self.zones_in, self.zones_out)):
            annotated_frame = sv.draw_polygon(
                annotated_frame, zone_in.polygon, COLORS.colors[i]
            )
            annotated_frame = sv.draw_polygon(
                annotated_frame, zone_out.polygon, COLORS.colors[i]
            )

        labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]
        annotated_frame = self.trace_annotator.annotate(annotated_frame, detections)
        annotated_frame = self.box_annotator.annotate(
            annotated_frame, detections, labels
        )

        for zone_out_id, zone_out in enumerate(self.zones_out):
            zone_center = sv.get_polygon_center(polygon=zone_out.polygon)
            if zone_out_id in self.detections_manager.counts:
                counts = self.detections_manager.counts[zone_out_id]
                for i, zone_in_id in enumerate(counts):
                    count = len(self.detections_manager.counts[zone_out_id][zone_in_id])
                    text_anchor = sv.Point(x=zone_center.x, y=zone_center.y + 40 * i)
                    annotated_frame = sv.draw_text(
                        scene=annotated_frame,
                        text=str(count),
                        text_anchor=text_anchor,
                        background_color=COLORS.colors[zone_in_id],
                    )

        return annotated_frame

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        results = self.model(
            frame, verbose=False, conf=self.conf_threshold, iou=self.iou_threshold
        )[0]
        detections = sv.Detections.from_ultralytics(results)
        detections.class_id = np.zeros(len(detections))
        detections = self.tracker.update_with_detections(detections)

        detections_in_zones = []
        detections_out_zones = []

        for i, (zone_in, zone_out) in enumerate(zip(self.zones_in, self.zones_out)):
            detections_in_zone = detections[zone_in.trigger(detections=detections)]
            detections_in_zones.append(detections_in_zone)
            detections_out_zone = detections[zone_out.trigger(detections=detections)]
            detections_out_zones.append(detections_out_zone)

        detections = self.detections_manager.update(
            detections, detections_in_zones, detections_out_zones
        )
        return self.annotate_frame(frame, detections)
