import pandas as pd
import numpy as np
import ast
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import pandas as pd
import numpy as np
import ast
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata
#Local imports
from Generic.Global.Borg import Borg


class TrajsProcessor (Borg):


    #Contextual generic objects
    __ctx = None

    #Configuration data
    __config = None

    #-----------------------------------------------------------------------------------------------------------------------------
    #Constructor
    def __init__(self, df):
        """
        Class builder, all the contextual configurations are charged from the base class (borg pattern) in a shared state
        Returns:
            [None]: None
        """
        #Setting contextual generic objects
        super().__init__()
        self.GP = self.ctx['__obj']['__global_procedures']
        self.df = df
        self.widths_objects = {"car": 1.8, "truck": 2, "van": 2.1, "bus": 2.6, "pedestrian": 0.6, "cyclist": 0.7, "tricyclist": 0.75, "motorcyclist": 0.8}
        self.length_objects = {"car": 4.5, "truck": 5.5, "van": 5.5, "bus": 12, "pedestrian": 0.6, "cyclist": 1.7, "tricyclist": 1.7, "motorcyclist": 2.2}
        self.grid_x = None
        self.grid_y = None
        self.scale_factor_map = None

    @staticmethod
    def safe_literal_eval(val):
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return val

    def preprocess(self):
        self.df['dir_vect'] = self.df['dir_vect'].apply(lambda x: self.safe_literal_eval(x) if pd.notnull(x) else x)
        self.df['mask'] = self.df['mask'].apply(lambda x: self.safe_literal_eval(x) if pd.notnull(x) else x)
        self.update_labels()
        self.smooth_time_series()

    def update_labels(self):
        grouped_df = self.df.groupby('id')
        mode_df = grouped_df.apply(self.get_mode).reset_index(drop=True)
        self.df = self.df.drop(columns=['label']).merge(mode_df[['id', 'label']], on='id', how='left')

    @staticmethod
    def get_mode(rows):
        if rows['obb_flag'].any():
            return rows[rows['obb_flag'] == True].mode().iloc[0]
        else:
            return rows[rows['obb_flag'] == False].mode().iloc[0]

    @staticmethod
    def calculate_centroid(mask):
        x_coords = [point[0] for point in mask]
        y_coords = [point[1] for point in mask]
        return np.mean(x_coords), np.mean(y_coords)

    def smooth_time_series(self):
        self.df = self.df.groupby('id').apply(self.weighted_rolling_mean).reset_index(drop=True)

    def weighted_rolling_mean(self, group):
        group['timestamp'] = pd.to_datetime(group['timestamp'], unit='ms')
        obb_true_rows = group[group['obb_flag']]
        if not obb_true_rows.empty:
            centroids = obb_true_rows['mask'].apply(self.calculate_centroid)
            avg_diff_x = (obb_true_rows['x'] - centroids.apply(lambda c: c[0])).mean()
            avg_diff_y = (obb_true_rows['y'] - centroids.apply(lambda c: c[1])).mean()
        else:
            avg_diff_x = 0
            avg_diff_y = 0

        group['x'] = group['x'] - avg_diff_x
        group['y'] = group['y'] - avg_diff_y
        group.set_index('timestamp', inplace=True)

        weights = np.where(group['obb_flag'], 5, 1)
        group['x'] = self.weighted_rolling_mean_series(group['x'], '800ms', weights)
        group['y'] = self.weighted_rolling_mean_series(group['y'], '800ms', weights)
        group['w'] = self.weighted_rolling_mean_series(group['w'], '1400ms', weights)
        group['h'] = self.weighted_rolling_mean_series(group['h'], '1400ms', weights)

        dir_vect_df = pd.DataFrame(group['dir_vect'].tolist(), index=group.index, columns=['dir_x', 'dir_y'])
        dir_vect_df['dir_x'] = dir_vect_df['dir_x'].rolling('800ms', center=True).mean()
        dir_vect_df['dir_y'] = dir_vect_df['dir_y'].rolling('800ms', center=True).mean()
        group['dir_vect'] = dir_vect_df[['dir_x', 'dir_y']].values.tolist()
        group.fillna(method='ffill', inplace=True)
        group.reset_index(inplace=True)
        return group

    @staticmethod
    def weighted_rolling_mean_series(series, window, weights):
        return series.rolling(window, center=True).apply(lambda x: np.average(x, weights=weights[:len(x)]), raw=True)

    def correct_by_velocity(self):
        self.calculate_scale_factor_map(sigma=2)

        # Calculate meters values and validate velocity
        self.df['scale_factor'] = griddata((self.grid_x.flatten(), self.grid_y.flatten()), self.scale_factor_map.flatten(), (self.df['x'], self.df['y']), method='linear')
        # Extract dx, dy components and apply scale factor
        self.df['dir_vect_dx'] = self.df['dir_vect'].apply(lambda vect: vect[0])
        self.df['dir_vect_dy'] = self.df['dir_vect'].apply(lambda vect: vect[1])
        self.df['dir_vect_dx'] = self.df['dir_vect_dx'] * self.df['scale_factor']
        self.df['dir_vect_dy'] = self.df['dir_vect_dy'] * self.df['scale_factor']
        self.df['dir_vect_m'] = self.df.apply(lambda row: np.array([row['dir_vect_dx'], row['dir_vect_dy']]), axis=1)
        self.df['velocity_km_per_h'] = self.df.apply(lambda row: np.linalg.norm(row['dir_vect_m']) * row['fps'] * 3.6, axis=1)
        self.df.drop(columns=['dir_vect_dx', 'dir_vect_dy', 'dir_vect_m'], inplace=True)

        # Correct the labels based on velocity
        avg_velocity = self.df.groupby('id')['velocity_km_per_h'].mean().reset_index()
        self.df = self.df.merge(avg_velocity, on='id', suffixes=('', '_avg'))
        self.df['corrected_label'] = self.df.groupby('id').apply(lambda group: group.apply(self.correct_label, axis=1)).reset_index(level=0, drop=True)
        self.df['label'] = self.df['corrected_label']
        self.df.drop(columns=['corrected_label', 'velocity_km_per_h_avg'], inplace=True)

    def correct_label(self, row):
        pedestrian_threshold = 8
        cyclist_threshold = 20
        avg_vel = row['velocity_km_per_h_avg']
        if row['label'] == 'pedestrian' and avg_vel > pedestrian_threshold:
            return 'cyclist'
        elif ((row['label'] == 'cyclist') or (row['label'] == 'pedestrian')) and avg_vel > cyclist_threshold:
            return 'motorcyclist'
        else:
            return row['label']

    def correct_coordinates(self):
        self.df = self.df.apply(self.correct_pedestrian_coordinates, axis=1)
        self.calculate_scale_factor_map(sigma=3)
        self.df['scale_factor'] = griddata((self.grid_x.flatten(), self.grid_y.flatten()), self.scale_factor_map.flatten(), (self.df['x'], self.df['y']), method='linear')

    def correct_pedestrian_coordinates(self, row):
        if row['label'] == 'pedestrian':
            mask = np.array(row['mask'])
            x_min = np.min(mask[:, 0])
            x_max = np.max(mask[:, 0])
            y_max = np.max(mask[:, 1])
            row['x'] = (x_min + x_max) / 2
            row['y'] = y_max
            row['w'] = row['w'] / 2
            row['h'] = row['w']
        return row

    def interpolate_data(self):
        self.df = self.split_dir_vect(self.df)
        # Calculate the sampling period in seconds
        self.df['sampling_period'] = 1 / self.df['fps']
        # Convert the sampling period to timedelta type
        self.df['sampling_period'] = pd.to_timedelta(self.df['sampling_period'], unit='s')
        self.df = self.df.groupby('id').apply(self.interpolate_group).reset_index(drop=True)
        self.df = self.combine_dir_vect(self.df)
        self.apply_nms_and_merge_ids()
        self.df['x_m'] = self.df['x'] * self.df['scale_factor']
        self.df['y_m'] = self.df['y'] * self.df['scale_factor']
        self.df['w_m'] = self.df['w'] * self.df['scale_factor']
        self.df['h_m'] = self.df['h'] * self.df['scale_factor']
        
        # Extract dx, dy components and apply scale factor
        self.df['dir_vect_dx'] = self.df['dir_vect'].apply(lambda vect: vect[0])
        self.df['dir_vect_dy'] = self.df['dir_vect'].apply(lambda vect: vect[1])
        self.df['dir_vect_dx'] = self.df['dir_vect_dx'] * self.df['scale_factor']
        self.df['dir_vect_dy'] = self.df['dir_vect_dy'] * self.df['scale_factor']
        self.df['dir_vect_m'] = self.df.apply(lambda row: np.array([row['dir_vect_dx'], row['dir_vect_dy']]), axis=1)
        self.df.drop(columns=['dir_vect_dx', 'dir_vect_dy'], inplace=True)

    @staticmethod
    def split_dir_vect(df):
        valid_dir_vect = df['dir_vect'].apply(lambda x: isinstance(x, list) and len(x) == 2)
        df = df[valid_dir_vect]
        dir_vect_df = df['dir_vect'].apply(pd.Series)
        dir_vect_df.columns = ['dir_vect_x', 'dir_vect_y']
        return pd.concat([df.drop(columns=['dir_vect']), dir_vect_df], axis=1)

    @staticmethod
    def combine_dir_vect(df):
        df['dir_vect'] = df[['dir_vect_x', 'dir_vect_y']].values.tolist()
        return df.drop(columns=['dir_vect_x', 'dir_vect_y'])

    def interpolate_group(self, group):
        group = group.set_index('timestamp')
        if len(group) < 2:
            return group
        oidx = group.index
        nidx = pd.date_range(oidx.min(), oidx.max(), freq= group['sampling_period'].iloc[0])
        interpolated_columns = {}
        for col in ['x', 'y', 'w', 'h', 'dir_vect_x', 'dir_vect_y', 'velocity_km_per_h', 'scale_factor']:
            interpolated_columns[col] = group[col].reindex(oidx.union(nidx)).interpolate('index').reindex(nidx)
        interpolated_group = pd.DataFrame(interpolated_columns, index=nidx)
        for col in ['id', 'label', 'fps', 'sampling_period', 'obb_flag', 'conf']:
            interpolated_group[col] = group[col].reindex(nidx, method='ffill')
        interpolated_group = interpolated_group.reset_index().rename(columns={'index': 'timestamp'})
        min_frame_ix = group['frame_ix'].min()
        interpolated_group['frame_ix'] = range(min_frame_ix, min_frame_ix + len(interpolated_group))
        return interpolated_group

    def apply_nms_and_merge_ids(self):
        def convert_to_xyxy(row):
            x, y, w, h = row['x'], row['y'], row['w'], row['h']
            r = np.arctan2(row['dir_vect'][1], row['dir_vect'][0])
            return self.GP.xywhr_to_xyxy((x, y, w, h, r))

        def process_group(group):
            boxes = group.apply(convert_to_xyxy, axis=1).tolist()
            scores = group['conf'].tolist()
            _, indices = self.GP.apply_nms(boxes, scores, iou_threshold=0.7)
            return group.iloc[indices]

        self.df = self.df.groupby('frame_ix').apply(process_group).reset_index(drop=True)

    def calculate_scale_factor_map(self, sigma):
        points = self.df[['x', 'y']].values
        values = self.df.apply(lambda row: (self.widths_objects.get(row['label']) / row['w'] + self.length_objects.get(row['label']) / row['h']) / 2, axis=1).values
        
        # Extend the grid by 100 pixels in both x and y directions
        x_min, x_max = self.df['x'].min() - 100, self.df['x'].max() + 100
        y_min, y_max = self.df['y'].min() - 100, self.df['y'].max() + 100
        
        self.grid_x, self.grid_y = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
        self.scale_factor_map = griddata(points, values, (self.grid_x, self.grid_y), method='linear')
        
        # Fill the extended areas with the nearest known scale factor values
        self.scale_factor_map = np.where(np.isnan(self.scale_factor_map), griddata(points, values, (self.grid_x, self.grid_y), method='nearest'), self.scale_factor_map)
        
        # Apply Gaussian filter to smooth the scale factor map
        self.scale_factor_map = gaussian_filter(self.scale_factor_map, sigma=sigma)



if __name__ == "__main__":
    trajs_processor = TrajsProcessor( pd.read_csv('output.csv') )
    trajs_processor.preprocess()
    trajs_processor.correct_by_velocity()
    trajs_processor.correct_coordinates()
    trajs_processor.interpolate_data()

    df = trajs_processor.df