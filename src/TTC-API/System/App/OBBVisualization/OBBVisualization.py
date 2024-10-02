import cv2
import numpy as np
import pandas as pd
#Local imports
from Generic.Global.Borg import Borg


class OBBVisualization (Borg):

    #Contextual generic objects
    __ctx = None

    #Configuration data
    __config = None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__(self, video_path, output_path, df):
        """
        Class builder, all the contextual configurations are charged from the base class (borg pattern) in a shared state
        Returns:
            [None]: None
        """
        #Setting contextual generic objects
        super().__init__()
        self.GP = self.ctx['__obj']['__global_procedures']
        self.video_path = video_path
        self.output_path = output_path
        self.df = df
        self.video = cv2.VideoCapture(video_path)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), self.fps, (self.frame_width, self.frame_height))
        self.labels_map = {label: idx for idx, label in enumerate(df['label'].unique())}
        self.colors = {class_id: (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)) for class_id in self.labels_map.keys()}

    #-----------------------------------------------------------------------------------------------------------------------------
    def process_video(self):
        frame_ix = 0
        ret, prev_frame = self.video.read()
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        while self.video.isOpened():
            ret, frame = self.video.read()
            if not ret:
                break

            frame_objects = self.df[self.df['frame_ix'] == frame_ix]

            if not frame_objects.empty:
                for _, obj in frame_objects.iterrows():
                    self.process_frame(frame, obj)

            self.out.write(frame)
            frame_ix += 1

        self.video.release()
        self.out.release()

    #-----------------------------------------------------------------------------------------------------------------------------
    def process_frame(self, frame, obj):
        x, y, w, h, dir_vect, label, track_id, velocity = obj['x'], obj['y'], obj['w'], obj['h'], obj['dir_vect'], obj['label'], obj['id'], obj['velocity_km_per_h']
        color = self.get_color(label)
        xywhr = (x, y, w, h, np.arctan2(dir_vect[1], dir_vect[0]))
        box = self.GP.xywhr_to_xyxyxyxy(xywhr)
        self.draw_labeled_polygon(frame, box, label, track_id, color, direction_vector=dir_vect, centroid=(x, y), velocity=velocity)

    #-----------------------------------------------------------------------------------------------------------------------------
    def get_color(self, class_id):
        return self.colors.get(class_id, (0, 0, 0))

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def draw_labeled_polygon(frame, box, label, track_id, color, direction_vector=None, centroid=None, velocity=None):
        cv2.polylines(frame, [np.array(box, np.int32).reshape((-1, 1, 2))], isClosed=True, color=color, thickness=2)
        label_text = f"{label} ID:{track_id}"
        if velocity is not None:
            label_text += f" Vel:{velocity:.2f} km/h"
        (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        cv2.rectangle(frame, (box[0][0], box[0][1] - 30), (box[0][0] + text_width, box[0][1]), color, cv2.FILLED)
        cv2.putText(frame, label_text, (box[0][0], box[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        if direction_vector is not None and centroid is not None:
            center_x, center_y = int(centroid[0]), int(centroid[1])
            end_x = int(center_x + direction_vector[0] * 10)
            end_y = int(center_y + direction_vector[1] * 10)
            cv2.arrowedLine(frame, (center_x, center_y), (end_x, end_y), color, 2, tipLength=0.5)



if __name__ == "__main__":
    video_path = '181653_cam3_bev.mp4'
    output_path = 'obb_processed.mp4'
    df = pd.read_csv('output.csv')  # Assuming the DataFrame is loaded from a CSV file
    obbvis = OBBVisualization(video_path, output_path, df)
    obbvis.process_video()