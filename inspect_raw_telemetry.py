#inspect the structural validity of the raw cvs file to understand timestamp frequencies and row structural health

import duckdb
import pandas as pd

DATA_PATH = "data/fusion_data_raw.csv"

def inspect_telemtry_health(file_path):
    print('=== Initialize Telemetry Audit Pipeline ===')

    con = duckdb.connect(database=':memory:')
    
    print("\n[1/2] Auditing Fleet Label & Fault State Distribution...")
    """
    * AVG(ErrRP) AS avg_roll_pitch_error: Attitude Control.
        * An elevated average here means the physical vehicle is failing to achieve its commanded orientation.
    * AVG(ErrYaw) AS avg_yaw_error: Heading Drift.
        * Large errors here point to magnetic interference or asymmetric motor thrust.
    * MAX(abAccX * abAccX + abAccY * abAccY + abAccZ * abAccZ) AS max_squared_shock: Scalar Vector Magnitudes.
        * Isolates the single largest combined 3D acceleration force in its squared form across all rows to maximize processing speed.
    * SQRT(max_squared_shock): Peak G-Force Conversion.
        * Converts that single worst-case squared shock value back into readable Earth G-forces to evaluate severe physical impact severity.
    """
    optimized_query = f"""
        WITH label_counts AS (
            SELECT 
                labels,
                COUNT(*) AS record_count,
                AVG(ErrRP) AS avg_roll_pitch_error,
                AVG(ErrYaw) AS avg_yaw_error,
                MAX(abAccX * abAccX + abAccY * abAccY + abAccZ * abAccZ) AS max_squared_shock
            FROM '{file_path}'
            GROUP BY labels
        )
        SELECT
            labels,
            record_count,
            ROUND((record_count *100.0)/SUM(record_count) OVER (), 2) AS percentage,
            ROUND(avg_roll_pitch_error, 4) AS avg_rp_error,
            ROUND(avg_yaw_error, 4) AS avg_yaw_error,
            ROUND(SQRT(max_squared_shock), 4) AS max_total_shock_g
        FROM label_counts
        ORDER BY labels ASC;
    """
    kinematic_df = con.execute(optimized_query).df()
    print(kinematic_df.to_string(index=False))

    #Timestamp structural check
    print("\n[2/2] Auditing Telemetry Frequency & Structural Time Gaps...")
    time_query = f"""
        WITH time_deltas AS (
            SELECT 
                timestamp,
                timestamp - LAG(timestamp) OVER (ORDER BY timestamp) AS delta_ms
            FROM '{file_path}'
        )
        SELECT 
            COUNT(*) AS total_sampled_records,
            MIN(delta_ms) AS min_time_gap_ms,
            MAX(delta_ms) AS max_time_gap_ms,
            ROUND(AVG(delta_ms), 2) AS avg_sensor_period_ms
        FROM time_deltas;
    """
    """
    * LAG(timestamp) OVER (ORDER BY timestamp): Chronological Step-Back.
        * Grabs the timing value from the immediate previous record to ensure we are comparing consecutive data points.
    * timestamp - LAG(timestamp): Delta Time Calculation.
        * Computes the exact millisecond gap between consecutive sensor updates to measure data stream continuity.
    * MIN(delta_ms) AS min_time_gap_ms: Double-Clipping Detector.
        * Identifies if any duplicate records were written at the exact same millisecond, signaling a logging system glitch.0 = duplicates
    * MAX(delta_ms) AS max_time_gap_ms: Packet Loss Evaluator.
        * Captures the longest period the vehicle went blind mid-flight, exposing critical communication drops or sensor blackouts.
    * ROUND(AVG(delta_ms), 2) AS avg_sensor_period_ms: Operational Frequency Baseline.
        * Calculates the steady operational update rate of the avionics stack to verify it is maintaining its required Hz frequency.
    """
    temporal_df = con.execute(time_query).df()
    print(temporal_df.to_string(index=False))

if __name__ == "__main__":
    inspect_telemtry_health(DATA_PATH)

