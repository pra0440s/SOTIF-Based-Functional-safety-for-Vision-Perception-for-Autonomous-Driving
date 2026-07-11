# SOTIF-Based-Functional-safety-for-Vision-Perception-for-Autonomous-Driving
## Purpose and scope of this document
This project documentation applies the structure and terminology of **ISO 21448 — Road vehicles — Safety of the Intended Functionality (SOTIF)** to a pedestrian-detection perception function, evaluated under synthetically generated adverse weather conditions (fog, snow, low-light).
 
This is an academic project to demonstrate the **process discipline** of SOTIF engineering: defining the Operational Design Domain (ODD), identifying functional insufficiencies and triggering conditions, evaluating risk, defining functional modifications, and proposing a verification & validation (V&V) strategy.
 
Where the project is a research effort rather than a released product.

## 1. Item Definition (Clause 6)

| Attribute | Description |
|---|---|
| **Item** | Camera-based pedestrian detection function |
| **Function** | Detect and localize pedestrians in the forward field of view of a monocular camera (JAAD dataset used monocular camera), output bounding boxes for downstream use (e.g. driver warning) |
| **Algorithm** | YOLO11l (You Only Look Once, v11, large variant) |
| **Sensing modality** | Single RGB camera (monocular), as sourced from JAAD |
| **Intended use** | Perception input to an ADAS pedestrian-protection function (e.g. forward collision warning / Automated Emergency Braking  |
| **Boundary of analysis** | Detection performance only — this project does not evaluate tracking, sensor fusion, or the downstream decision/actuation logic |

## 2. Clause 6 — SOTIF Engineering Cycle: ODD Definition, Hazard Identification, and Risk Evaluation

The project follows the SOTIF "specify → identify → evaluate → mitigate → verify/validate" cycle:

```mermaid
flowchart LR

subgraph Specify
    A[Item Definition]
    B[ODD Definition]
end

subgraph Identify
    C[Hazard Identification and Risk Evaluation]
    D[Functional Insufficiency and Triggering Condition Identification]
end

subgraph Mitigate
    E[Functional Modification]
end

subgraph Verify_Validate
    F[Verification of Modifications]
    G[Verification of Known Scenarios]
    H[Validation of Residual Risk]
end

A --> B
B --> C
C --> D
D --> E
E --> F
F --> G
G --> H
H -->|Residual risk not acceptable| D
```

### 6.2 Operational Design Domain (ODD) Definition
 
The ODD constrains the conditions under which the pedestrian-detection function is claimed to operate as intended.
 
| ODD dimension | Definition for this project |
|---|---|
| **Road type** | Urban/suburban roads (as represented in JAAD) |
| **Scenery** |  crosswalk with pedestrian presence |
| **Lighting** | Daylight (nominal), low-light as edge/adverse condition |
| **Weather** | Clear (nominal), fog and snow as adverse conditions under evaluation |
| **Sensor state** | Single forward-facing camera, no lens obstruction or physical degradation modeled |
| **Traffic participants** | Pedestrians only (in-scope); vehicles/cyclists out of scope for this iteration |

**Nominal ODD** = clear weather, daylight.
**Adverse/edge-of-ODD conditions under test** = fog, snow, darkness — synthetically injected via `imagecorruptions` and custom gamma reduction (`fog.py`, `snow.py`, `dark.py`).
 
### 6.3 Hazard Identification
 
| Hazard ID | Hazardous behavior | Potential harm |
|---|---|---|
| H-01 | Failure to detect a present pedestrian (false negative) | Collision with pedestrian |
| H-02 | Late detection (correct detection, but too late for safe reaction) | Reduced time-to-react, possible collision |
| H-03 | flickering detection | Delayed warning/braking |
| H-04 | False positive detection  | Unnecessary braking, potential rear-end collision (out of scope for detection-only eval, noted for completeness) |

### 6.4 Risk Evaluation (Qualitative)
 
Using a simplified severity/exposure/controllability rationale (correpomdent to ISO 26262 ASIL reasoning):
 
| Hazard | Severity | Exposure (adverse weather + pedestrian present) | Controllability (by driver/system) | Qualitative risk |
|---|---|---|---|---|
| H-01 (missed detection) | High (potential fatality) | Medium (weather events + pedestrian co-occurrence) | Low (driver may have no cue) | **High priority** |
| H-02 (late detection) | High | Medium | Low–Medium | **High priority** |
| H-03 (flicker) | Medium | Medium | Medium | Medium priority |


### 6.5 SOTIF Area Classification (Known/Unknown × Safe/Unsafe)
 
ISO 21448 frames the entire scope of a function's behavior space into four areas. The purpose of the SOTIF process as a whole is to move scenarios from Area 3 into Area 2 (via analysis), and from Area 2 into Area 1 (via mitigation and verification) — the residual size of Areas 2 and 3 is the actual safety argument.

| Area | Definition | This project's mapping |
|---|---|---|
| **Area 1 — Known Safe** | Identified scenarios where the function is shown to behave safely | Clear-weather / daylight detection on `video_0232`, where YOLO11l meets acceptable recall/precision (pending measured baseline) |
| **Area 2 — Known Unsafe** | Identified scenarios where the function is shown to behave unsafely | Fog, snow, and dark conditions where recall drops and H-01/H-02 (missed/late detection) are observed — this is the direct output of the Clause 6/7/10 evaluation in this project |
| **Area 3 — Unknown Unsafe** | Scenarios not yet identified/tested, where the function would fail if tested | Not covered by this project: e.g. rain, fog+darkness combined, partial occlusion by other objects, non-JAAD scenes, different camera/sensor hardware, other pedestrian poses/clothing not represented in `video_0232` |
| **Area 4 — Unknown Safe / Irrelevant** | Scenarios not tested, but genuinely safe or outside the ODD | scenarios entirely outside the defined ODD, such as off-road or highway-only driving with no pedestrian exposure |

## Future Work
