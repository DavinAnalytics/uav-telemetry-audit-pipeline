# UAV Mission Reliability Testing & Telemetry Audit Automation

**Author:** Davin Kim  
**Core Infrastructure:** DuckDB (SQL) · Python (pandas) · Conda · PowerShell  
**Frontend Stack:** Streamlit (Operations UI) · HTML5/CSS3/JS (GitHub Pages Executive Briefing)

---

## Why clean dashboards fail rugged robots

Most data analytics portfolios are built for the cloud, tracking clean consumer transactions, e-commerce clicks, or predictable SaaS metrics.

Physical robots don't live in the cloud. When an autonomous platform operates at the edge in unstructured, GPS-denied environments, a sensor failure isn't a database anomaly; it can take the vehicle offline mid-operation. If a drone or quadruped experiences thrust degradation, localized stabilization collapse, or structural impact mid-mission, a field operations team can't spend hours parsing a sub-second, multi-sensor fused telemetry log with hundreds of variables.

This project builds a local data pipeline that ingests 12,253 rows of high-frequency kinematic telemetry (`fusion_data_raw.csv`), isolates physical failure modes through time-series feature engineering, downsamples edge noise into human-scale windows, and produces an interactive triage dashboard that ops teams can use during incident review.

---

## Local execution architecture

This system runs entirely locally, bypassing cloud warehouses. That matters when edge-collected data carries operational constraints or simply doesn't belong on a third-party platform.

- DuckDB runs an embedded, vectorized execution engine in-memory inside a local Python process, handling complex analytical queries on raw CSV data at native C++ speed.
- A Conda environment (`uav-env`) on Windows 10 manages dependencies without affecting system-level packages.
- Streamlit reads directly from the engineered data layer, using `@st.cache_data` to avoid redundant disk I/O during UI interactions.

---

## Technical findings & kinematic insights

The telemetry audit identified **189 anomalous seconds** across the active flight timeline, mapping four distinct fault signatures from sensor variance and vector limits:

### Flight leg failure signatures

- **Label 1 (Attitude Drift):** Minor tracking deviations where actual orientation drifted slightly from commanded paths (`avg_rp_error: 0.0417`). These are normal closed-loop adjustments under localized loads like crosswinds, not failure states.
- **Label 2 (Critical Oscillation & Structural Shock):** Major hardware instability. Autopilot tracking errors jumped roughly 10x ($0.4292$), with a peak mechanical shock vector of **89.42 Gs**. That combination points to a severe structural impact or aerodynamic control loop breakdown.
- **Label 3 (Actuator Saturation):** Localized component strain. Tracking errors increased slightly ($0.0532$) while peak mechanical shock was the lowest across all fault categories ($10.42$ Gs). This pattern isolates a motor working at maximum thermal output to hold the platform airborne without causing immediate structural damage.
- **Label 4 (Avionics Freeze / Dead State):** A software lockup. Autopilot tracking errors dropped to exactly **0.0000**. A moving aerial vehicle navigating 3D space never achieves perfect zero error against its target; this reading means the flight controller froze and locked its last known state.

### Data pipeline & temporal integrity

- **Duplicate frames detected:** The pipeline caught a minimum time step of `0.0 ms`, confirming the hardware logger recorded duplicate sensor frames at identical millisecond marks.
- **Workshop gap isolated:** The temporal audit found a maximum consecutive time gap of **8,149,655.5 ms (~2.26 hours)**, corresponding to a non-flight bench period. A sanitization filter of `delta_ms < 500,000` removes this gap before any downstream visualization.

---

## Feature engineering & SQL optimizations

### Vector magnitude optimization (kinetic shock)

Computing the 3D Euclidean vector magnitude ($\|v\| = \sqrt{x^2 + y^2 + z^2}$) row-by-row across 12,253 records is slow when `SQRT` runs on every entry. The pipeline instead computes the squared magnitude ($x^2 + y^2 + z^2$) inside a Common Table Expression first. Because squaring preserves relative ordering ($A > B \iff A^2 > B^2$), the database finds the maximum squared value at full speed and applies `SQRT` only once per grouped category.

### Dual independent axis scale design

Standard single-axis charts break down when plotted variables differ by orders of magnitude. Peak mechanical shock reaches **89.42 Gs**; tracking errors range between `0.0` and `0.43`. On a shared axis, the error line flattens to an unreadable baseline.

The operations interface splits these into independent layout columns with separate vertical scales. This makes the correlation visible: the structural trauma spike and the tracking error explosion occur at the same millisecond.

---

## User interfaces and deployment

The frontend targets two different users with separate tools.

### Operations tool (Streamlit)

An interactive utility for support and dispatch teams working an active maintenance ticket. The sidebar displays a real-time anomaly count, a priority selector (`High`, `Medium`, `Low`), a "Mark as Reviewed" toggle, and a technician notes field. The main view groups raw high-frequency data into 1-second buckets, averaging tracking errors to observe systematic drift while preserving maximum acceleration force so impact spikes are never averaged out.

### Executive summary (GitHub Pages)

A single-page artifact for engineering managers and stakeholders who need to review vehicle flight health without running a local environment. It includes CSS keyframe animations showing vehicle pitch/roll drift and high-frequency structural vibration, with a button linking to the Streamlit dashboard.

---

## Quickstart

Run these commands in PowerShell:

```powershell
# 1. Clone the repository
git clone https://github.com/DavinAnalytics/uav-telemetry-audit-pipeline.git
cd uav-telemetry-audit-pipeline

# 2. Set up the Conda environment
conda create -n uav-env python=3.11 -y
conda activate uav-env

# 3. Install core dependencies
pip install pandas duckdb pyarrow streamlit

# 4. Run the data pipeline to generate sanitized output
python build_telemetry_rules.py

# 5. Launch the triage dashboard
streamlit run app.py
```
