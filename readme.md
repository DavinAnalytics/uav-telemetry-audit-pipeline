# Mission Reliability Testing & Telemetry Audit Automation


**Author:** Davin Kim  
**Core Infrastructure:** DuckDB (SQL) · Python (pandas) · Conda · PowerShell  
**Frontend Stack:** Streamlit (Operations UI) · HTML5/CSS3/JS (GitHub Pages Executive Briefing)

---

## Why clean dashboards fail rugged robots

Most data analytics portfolios are built for the cloud, tracking clean consumer transactions, e-commerce clicks, or predictable SaaS metrics.

Physical robots don't live in the cloud. When an autonomous platform operates at the edge in unstructured, GPS-denied environments, a sensor failure isn't a database anomaly; it can take the vehicle offline mid-operation. If a drone or quadruped experiences thrust degradation, localized stabilization collapse, or structural impact mid-mission, a field operations team can't spend hours parsing a sub-second, multi-sensor fused telemetry log with hundreds of variables.

This project builds a local data pipeline that ingests 12,253 rows of high-frequency kinematic telemetry (`fusion_data_raw.csv`), isolates physical failure modes through time-series feature engineering, downsamples edge noise into human-scale windows, and ships an interactive Fleet Operations Portal that ops and support teams can actually use during triage.

---

## Local execution architecture

This system bypasses cloud warehouses entirely. Everything runs locally, which matters when you're working against edge-collected data that doesn't belong in a managed service.

- DuckDB runs embedded SQL validation scripts inside a PowerShell workflow on Windows 10, keeping schema checks fast and offline.
- The kinematic engineering layer is isolated inside a Conda environment in VS Code, using pandas for rolling time-series calculations.
- The Fleet Operations UI is a Streamlit tool built for ops and support teams actively reviewing fleet status.
- The executive summary is a single-page web artifact on GitHub Pages that translates drone physics into structured insights for engineering managers and stakeholders.

---

## Kinematic feature engineering

The raw telemetry log captures 19 distinct metrics across space, orientation, and force. Three calculated dimensions turn those variables into failure indicators.

### Absolute attitude drift tracking

Autonomous systems track the gap between commanded and executed motion. Persistent divergence usually means sensor degradation or physical stress. The pipeline computes the absolute deviation between what the onboard system intended and what the hardware actually did:

$$\text{Drift}_{\text{Roll}} = |\text{DesRoll} - \text{Roll}|$$
$$\text{Drift}_{\text{Pitch}} = |\text{DesPitch} - \text{Pitch}|$$

### Total kinetic shock

Individual X, Y, and Z accelerometer readings don't flag multidimensional impacts well. This pipeline tracks total G-force events across all structural axes simultaneously:

$$\text{Total G} = \sqrt{\text{abAccX}^2 + \text{abAccY}^2 + \text{abAccZ}^2}$$

In smooth flight, Total G sits near 9.81 m/s² (gravity). Violent deviations flag physical collisions or structural drops.

### Time-window alignment

Raw edge logs operate at sub-second frequency. The pipeline aggregates them into 1-second rolling averages, which keeps the dashboard responsive and separates micro-level debugging from fleet-level triage.

---

## Empirical anomaly signatures

Running statistical aggregations over the target data reveals distinct structural signatures for each fault state:

| Operational label | Telemetry signature | Physical root cause |
| :--- | :--- | :--- |
| **Label 0: Normal** | Stable attitude tracks; Total G ≈ 9.81 m/s²; minimal error drift. | Nominal flight performance. |
| **Label 1: Fault** | `abAccX` drops to a mean of -4.71 m/s². | Longitudinal propulsion deficit: extreme deceleration or heavy drag. |
| **Label 2: Fault** | Onboard errors (`ErrRP`) surge 10x to 0.43; Roll variance explodes to 24.03. | Kinematic stabilization collapse: localized control surface failure. |
| **Label 4: Fault** | `ErrRP` falls to 0.00; `abAccZ` locks at -9.84 m/s² (σ = 1.13). | Sensor freeze or post-impact static: landed, static, or complete sensor lock. |

---

## User interfaces and deployment

The frontend is split into two environments because the audiences are different.

### Operations tool (Streamlit)

An internal utility for support and dispatch teams actively working a case.

- Interactive flight matrix plots tracking errors against live accelerometer bounds across a configurable time window.
- A sidebar triage panel where ops personnel can set incident ticket priority (High, Medium, Low) and log review status through a checkbox (`[ ] Mark as reviewed by ops`).

### Executive summary (GitHub Pages)

A single-page artifact for engineering managers and stakeholders who need to understand what happened without running any code.

- Interactive script components visualize spatial vehicle physics as telemetry error flags change, so structural tilting is shown rather than described.
- Ends with a direct link to the live Streamlit tool for anyone who wants to go deeper.

---

## Quickstart

To run the pipeline and dashboard locally on Windows, execute these commands in PowerShell in order:

```powershell
# 1. Clone the repository
git clone https://github.com/yourusername/uav-telemetry-pipeline.git
cd uav-telemetry-pipeline

# 2. Set up a Conda environment
conda create -n uav-env python=3.11
conda activate uav-env

# 3. Install dependencies
pip install -r requirements.txt


```
