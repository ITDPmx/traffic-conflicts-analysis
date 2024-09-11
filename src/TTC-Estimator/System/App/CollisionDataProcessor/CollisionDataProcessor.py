import pandas as pd
import numpy as np
import sys
from itertools import combinations
#local imports
from System.App.TwoDimTTC import TwoDimTTC 
from Generic.Global.Borg import Borg


class CollisionDataProcessor (Borg):

    #Contextual generic objects
    __ctx = None

    #Configuration data
    __config = None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__(self, df):
        """
        Class builder, all the contextual configurations are charged from the base class (borg pattern) in a shared state
        Returns:
            [None]: None
        """
        #Setting contextual generic objects
        super().__init__()
        self.df = df.copy()
        self.pairs = None
        self.severity_df= None
        self.grouped_df = None

    def calculate_velocity(self, group):
        group = group.sort_values(by='timestamp')
        group[['hx', 'hy']] = pd.DataFrame(group['dir_vect_m'].tolist(), index=group.index)
        frame_period = group['sampling_period'].iloc[0].total_seconds()  
        group['vx'] = group['hx'] / frame_period
        group['vy'] = group['hy'] / frame_period
        return group

    def preprocess_data(self):
        self.df = self.df.groupby('id').apply(self.calculate_velocity).reset_index(drop=True)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['seconds'] = self.df['timestamp'].dt.second
        self.df['milliseconds'] = self.df['timestamp'].dt.microsecond // 1000
        self.df['timestamp'] = self.df['seconds'] + self.df['milliseconds'] / 1000
        self.df.drop(columns=['seconds', 'milliseconds'], inplace=True)

    def generate_pairs(self):
        pairs = []
        for _, group in self.df.groupby('frame_ix'):
            ids = group['id'].tolist()
            for (id_i, id_j) in combinations(ids, 2):
                vehicle_i = group[group['id'] == id_i]
                vehicle_j = group[group['id'] == id_j]
                pair = {
                    'timestamp': vehicle_i['timestamp'].values[0],
                    'id_i': id_i,
                    'x_i': vehicle_i['x_m'].values[0],
                    'y_i': vehicle_i['y_m'].values[0],
                    'vx_i': vehicle_i['vx'].values[0],
                    'vy_i': vehicle_i['vy'].values[0],
                    'hx_i': vehicle_i['hx'].values[0],
                    'hy_i': vehicle_i['hy'].values[0],
                    'length_i': vehicle_i['h_m'].values[0],
                    'width_i': vehicle_i['w_m'].values[0],
                    'velocity_i_kmh': vehicle_i['velocity_km_per_h'].values[0],  
                    'conf_i': vehicle_i['conf'].values[0],
                    'class_i': vehicle_i['label'].values[0],
                    'id_j': id_j,
                    'x_j': vehicle_j['x_m'].values[0],
                    'y_j': vehicle_j['y_m'].values[0],
                    'vx_j': vehicle_j['vx'].values[0],
                    'vy_j': vehicle_j['vy'].values[0],
                    'hx_j': vehicle_j['hx'].values[0],
                    'hy_j': vehicle_j['hy'].values[0],
                    'length_j': vehicle_j['h_m'].values[0],
                    'width_j': vehicle_j['w_m'].values[0],
                    'velocity_j_kmh': vehicle_j['velocity_km_per_h'].values[0],
                    'conf_j': vehicle_j['conf'].values[0],
                    'class_j': vehicle_j['label'].values[0] 
                }
                pairs.append(pair)
        self.pairs = pd.DataFrame(pairs)

    def calculate_ttc(self):
        samples = TwoDimTTC.TTC(self.pairs, 'dataframe')
        self.severity_df = samples.copy()

    @staticmethod
    def quadratic_function(ttc, velocity):
        return (27.0011 - 2.0031 * ttc + 0.0461 * velocity
                - 0.0002 * ttc**2 + 0.0001 * ttc * velocity
                + 0.0003 * velocity**2)

    def calculate_severity(self):
        self.severity_df['severity_ij'] = self.severity_df.apply(lambda row: self.quadratic_function(row['TTC_ij'], row['velocity_i_kmh']), axis=1)
        self.severity_df['severity_ji'] = self.severity_df.apply(lambda row: self.quadratic_function(row['TTC_ji'], row['velocity_j_kmh']), axis=1)

    def filter_data(self):
        self.severity_df = self.severity_df[((self.severity_df['TTC_ij'] > 0) | (self.severity_df['TTC_ji'] > 0)) &
                                            ((self.severity_df['TTC_ij'] != float('inf')) | (self.severity_df['TTC_ji'] != float('inf'))) &
                                            ((self.severity_df['severity_ij'] > 0) | (self.severity_df['severity_ji'] > 0))]
        numeric_cols = self.severity_df.select_dtypes(include=['number']).columns
        self.severity_df[numeric_cols] = self.severity_df[numeric_cols].apply(pd.to_numeric, errors='ignore', downcast='float')

    @staticmethod
    def mean(series):
        return series.replace([-1, float('inf')], np.nan).dropna().mean()

    @staticmethod
    def std(series):
        return series.replace([-1, float('inf')], np.nan).dropna().std()

    @staticmethod
    def median(series):
        return series.replace([-1, float('inf')], np.nan).dropna().median()

    @staticmethod
    def min(series):
        return series.replace([-1, float('inf')], np.nan).dropna().min()

    @staticmethod
    def max(series):
        return series.replace([-1, float('inf')], np.nan).dropna().max()

    def aggregate_data(self):
        self.grouped_df = self.severity_df.groupby(['id_i', 'id_j']).agg({
            'class_i': 'first',
            'class_j': 'first',
            'severity_ij': [self.mean, self.std, self.median, self.min, self.max],
            'severity_ji': [self.mean, self.std, self.median, self.min, self.max],
            'TTC_ij': [self.mean, self.std, self.median, self.min, self.max],
            'TTC_ji': [self.mean, self.std, self.median, self.min, self.max]
        }).reset_index()

        self.grouped_df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in self.grouped_df.columns]
        self.grouped_df.rename(columns={'id_i_': 'id_i', 'id_j_': 'id_j', 'class_i_first': 'class_i', 'class_j_first': 'class_j'}, inplace=True)

        max_severity_idx_ij = self.severity_df.groupby(['id_i', 'id_j'])['severity_ij'].idxmax()
        max_severity_idx_ji = self.severity_df.groupby(['id_i', 'id_j'])['severity_ji'].idxmax()
        max_severity_idx = max_severity_idx_ij.combine_first(max_severity_idx_ji)

        max_severity_df = self.severity_df.loc[max_severity_idx, ['id_i', 'id_j', 'timestamp', 'velocity_i_kmh', 'velocity_j_kmh']]
        max_severity_df.columns = ['id_i', 'id_j', 'timestamp_max_severity', 'velocity_i_kmh_max_severity', 'velocity_j_kmh_max_severity']

        self.grouped_df = pd.merge(self.grouped_df, max_severity_df, on=['id_i', 'id_j'], how='left')

        columns_to_remove = ['x', 'y', 'vx', 'hx', 'hy', 'length', 'width']
        self.grouped_df = self.grouped_df.drop(columns=columns_to_remove, errors='ignore')
        self.grouped_df = self.grouped_df[['id_i', 'id_j', 'timestamp_max_severity', 'class_i', 'class_j', 'severity_ij_mean', 'severity_ij_std', 'severity_ij_median', 'severity_ij_min', 'severity_ij_max', 'severity_ji_mean', 'severity_ji_std', 'severity_ji_median', 'severity_ji_min', 'severity_ji_max', 'TTC_ij_mean', 'TTC_ij_std', 'TTC_ij_median', 'TTC_ij_min', 'TTC_ij_max', 'TTC_ji_mean', 'TTC_ji_std', 'TTC_ji_median', 'TTC_ji_min', 'TTC_ji_max', 'velocity_i_kmh_max_severity', 'velocity_j_kmh_max_severity']]
        numeric_cols = self.grouped_df.select_dtypes(include=['number']).columns
        self.grouped_df[numeric_cols] = self.grouped_df[numeric_cols].apply(pd.to_numeric, errors='ignore', downcast='float')

    def save_to_csv(self, collision_data_path='reports/collision_data.csv', summary_data_path='reports/collision_data_summary.csv'):
        self.severity_df.to_csv(collision_data_path, index=False)
        self.grouped_df.to_csv(summary_data_path, index=False)

if __name__ == "__main__":
    df = pd.read_csv('output.csv')  # Assuming the DataFrame is loaded from a CSV file
    processor = CollisionDataProcessor(df)
    processor.preprocess_data()
    processor.generate_pairs()
    processor.calculate_ttc()
    processor.calculate_severity()
    processor.filter_data()
    processor.aggregate_data()
    processor.save_to_csv()