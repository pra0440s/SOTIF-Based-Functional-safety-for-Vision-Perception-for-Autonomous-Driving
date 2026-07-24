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


<div align="center">
  <h3>Fog Severity Comparison</h3>
  <table>
    <tr>
      <th>orginal picture</th>
      <th>Severity 1</th>
      <th>Severity 2</th>
      <th>Severity 3 </th>
      <th>Severity 4 </th>
      <th>Severity 5</th>
    </tr>
    <tr>
      <td><img width="203" height="345" alt="image" src="https://github.com/user-attachments/assets/fe8ca943-6374-4092-9d68-54aa4fe98c41" /></td>
      <td><img width="223" height="374" alt="fog s1" src="https://github.com/user-attachments/assets/71304911-73f9-40bc-b9f0-97caf8dc1f04" /></td>
      <td><img width="220" height="389" alt="fog s2" src="https://github.com/user-attachments/assets/71b6f5f1-a943-4b78-ad06-06938cc38b0a" /></td>
      <td><img width="215" height="364" alt="fog s3" src="https://github.com/user-attachments/assets/77cf604b-da66-4bd4-b62b-b00a248cd829" /></td>
      <td><img width="229" height="368" alt="fog s4" src="https://github.com/user-attachments/assets/9a7f96c8-a2f1-4859-af62-7584c072c930" /></td>
      <td><img width="224" height="380" alt="fog s5" src="https://github.com/user-attachments/assets/6740a5a3-b662-4ca6-a63b-693aa6f38037" /></td>
    </tr>
  </table>

  <br>

  <h3>Snow Severity Comparison</h3>
  <table>
    <tr>
      <th>orginal picture</th>
      <th>Severity 1</th>
      <th>Severity 2</th>
      <th>Severity 3 </th>
      <th>Severity 4 </th>
      <th>Severity 5</th>
    </tr>
    <tr>
      <!-- REPLACE THE 'src' LINKS BELOW WITH YOUR SNOW IMAGE ASSET LINKS -->
      <td><img width="203" height="345" alt="image" src="https://github.com/user-attachments/assets/fe8ca943-6374-4092-9d68-54aa4fe98c41" /></td>
      <td><img width="222" height="407" alt="snow s1" src="https://github.com/user-attachments/assets/81452d1b-f839-4b7a-9089-41feb6831f8d" /></td>
      <td><img width="218" height="380" alt="snow s2" src="https://github.com/user-attachments/assets/27c9eef7-da41-4044-9d35-a3e7bf2e36c7" /></td>
      <td><img width="224" height="422" alt="snow s3" src="https://github.com/user-attachments/assets/05548908-ca3e-48d4-af84-6f72e91de102" /></td>
      <td><img width="229" height="392" alt="snow s4" src="https://github.com/user-attachments/assets/a2260feb-bf0e-4520-9e05-39b3f37a6a26" /></td>
      <td><img width="209" height="373" alt="snow s5" src="https://github.com/user-attachments/assets/9f9a2e36-c365-40f3-b5b3-636be82a7d0c" /></td>
    </tr>
  </table>
</div>










 
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

How this project moves the needle:

Before this work: fog/snow degradation on this pedestrian-detection model was unknown (Area 3 or 4, undetermined) nobody had measured it.
After this work: it becomes known — specifically Area 2 (Known Unsafe), because the evaluation shows degraded recall under these conditions. That reclassification, from unknown to known-unsafe, is the safety-relevant contribution of a SOTIF evaluation project, even before any fix is implemented.

### 3. Clause 7 — Identification and Evaluation of Functional Insufficiencies and Triggering Conditions
### 3.1 Functional Insufficiencies
Per ISO 21448 terminology, a functional insufficiency is either an insufficiency of specification or a performance insufficiency. For this system:

- FI-01 (performance insufficiency): YOLO11l's feature extraction degrades under reduce visibility (fog), reducing objectness confidence below the detection threshold.
- FI-02 (insufficiency of specification): The model's confidence threshold was tuned for clean and daylight conditions and is not adapted per-condition, so a single static threshold is itself a specification gap.

### 3.2 Triggering Conditions

A triggering condition is the specific circumstance that activates a functional insufficiency into a hazardous behavior.
| Triggering condition | Linked FI | Description |
|---|---|---|
| TC-01 | FI-01 | Fog density above a level that reduces scene contrast beyond model's training distribution |
| TC-02 | FI-02 | Snowfall particle density overshadowing pedestrian visibility |

### 3.3 FTA Analysis
```mermaid
flowchart TD
    TE["Top Event<br/>Missed Pedestrian Detection"]

    OR1{{OR}}
    OR2{{OR}}
    OR3{{OR}}

    TE --> OR1
    TE --> OR2
    TE --> OR3

    OR1 --> AND1{{AND}}
    OR1 --> AND2{{AND}}
    OR1 --> AND3{{AND}}

    AND1 --> FOG["Fog reduces image contrast"]
    AND1 --> PED1["Pedestrian present"]

    AND2 --> SNOW["Snow occludes pedestrian"]
    AND2 --> PED2["Pedestrian present"]

    AND3 --> DARK["Low illumination"]
    AND3 --> PED3["Pedestrian present"]

    OR2 --> TH["Static confidence threshold too high"]

    OR3 --> GT["Ground-truth / annotation misalignment"]
```
## 4. Clause 8 — Functional Modification
 
Per ISO 21448, once functional insufficiencies and triggering conditions are identified, **functional modifications** are proposed to reduce risk. These may be specification changes, design changes, or ODD restrictions — not just "make the model better."
 
| Modification ID | Type | Description | Linked to |
|---|---|---|---|
| FM-01 | Design change (sensor redundancy) | Add a Radar sensor modality less affected by fog and fuse with camera output, so a fog-degraded camera detection can be backed up by another sensor | FI-01 |
| FM-02 | Design change (algorithmic) | retrain YOLO11l on fog-augmented training data (domain adaptation) so feature extraction is more robust to low-visibility inputs | FI-01 |
| FM-03 |	Design change (adaptive thresholding) | Replace the static confidence threshold with one conditioned on an estimated visibility/weather class (e.g. lower threshold when fog is detected, since true positives will naturally have lower confidence) | FI-02 |
| FM-04 | ODD restriction (fallback)e | If neither FM-01 nor FM-03 is feasible, restrict the ODD to require reduced automation/driver takeover when visibility estimate drops below a defined level | FI-01 |

 
 
---

## Future Work
