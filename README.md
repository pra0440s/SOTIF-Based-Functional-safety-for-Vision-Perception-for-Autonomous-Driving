# SOTIF-Based-Functional-safety-for-Vision-Perception-for-Autonomous-Driving
## Project Overview
This project implements a SOTIF (ISO 21448)-based safety evaluation framework for camera-based object detection systems used in autonomous driving. The objective is to analyze the safety limitations of YOLOv11pt under challenging perception conditions such as occlusion, fog, rain, low light, and motion blur.

Instead of focusing only on detection accuracy, this project emphasizes safety-critical failure analysis by identifying hazardous scenarios and evaluating perception reliability under degraded conditions.

## Objectives
- Evaluate robustness of YOLOv8 object detection under adverse conditions
- Generate synthetic safety-critical driving scenarios using imagecorruption / Albumentations.
- Classify scenarios based on SOTIF concepts:
   - Known Safe
   - Known Unsafe
   - Unknown Unsafe



## Methodology
### 1. Baseline Detection
- Run YOLOv11pt on standard driving Video (JAAD dataset)
- Record detection results and confidence scores



### 2. Scenario Generation

Adverse scenarios are created using imagecorruption / Albumentations:

--  🌫️ Fog simulation

--  ❄️ snow effects

-- 🌑 Low illumination (night conditions)



### 3. Object Detection

 - Apply YOLOv11pt on one modified scenario.
 - Extract Frames, bounding boxes, class labels, and confidence scores


## Tools & Technologies
- Python
- YOLOv8 (Ultralytics)
- OpenCV
- Albumentations / Image corruption
- NumPy 


## Future Work
