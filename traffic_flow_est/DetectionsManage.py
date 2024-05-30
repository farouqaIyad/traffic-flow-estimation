from typing import Dict, List, Set, Tuple
import supervision as sv
import numpy as np


class DetectionsManager:
    def __init__(self) -> None:
        self.tracker_id_to_zone_id: Dict[int, int] = {}
        self.counts: Dict[int, Dict[int, Set[int]]] = {}

    def update(
        self,
        detections_all: sv.Detections,
        detections_in_zones: List[sv.Detections],
        detections_out_zones: List[sv.Detections],
    ) -> sv.Detections:

        for zone_in_id, detections_in_zone in enumerate(detections_in_zones):

            for tracker_id in detections_in_zone.tracker_id:
                print(zone_in_id)
                self.tracker_id_to_zone_id.setdefault(tracker_id, zone_in_id)

        for zone_out_id, detections_out_zone in enumerate(detections_out_zones):
            for tracker_id in detections_out_zone.tracker_id:
                if tracker_id in self.tracker_id_to_zone_id:
                    zone_in_id = self.tracker_id_to_zone_id[tracker_id]
                    self.counts.setdefault(zone_out_id, {})
                    self.counts[zone_out_id].setdefault(zone_in_id, set())
                    self.counts[zone_out_id][zone_in_id].add(tracker_id)

        detections_all.class_id = np.vectorize(
            lambda x: self.tracker_id_to_zone_id.get(x, -1)
        )(detections_all.tracker_id)
        return detections_all[detections_all.class_id != -1]
