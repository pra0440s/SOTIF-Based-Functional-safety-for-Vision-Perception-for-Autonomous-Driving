import cv2
import csv
import json
import argparse
import numpy as np
from ultralytics import YOLO
 
 
def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
 
    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h
 
    if inter_area == 0:
        return 0.0
 
    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
 
    return inter_area / float(areaA + areaB - inter_area)
 
 
def match_boxes(pred_boxes, gt_boxes, iou_thresh=0.7):
    """
    Greedy IoU matching between predicted and GT boxes for one frame.
    Returns (tp, fp, fn) counts.
    """
    matched_gt = set()
    tp = 0
 
    for pbox in pred_boxes:
        best_iou = 0.0
        best_idx = -1
        for idx, gbox in enumerate(gt_boxes):
            if idx in matched_gt:
                continue
            i = iou(pbox, gbox)
            if i > best_iou:
                best_iou = i
                best_idx = idx
 
        if best_iou >= iou_thresh and best_idx != -1:
            matched_gt.add(best_idx)
            tp += 1
 
    fp = len(pred_boxes) - tp
    fn = len(gt_boxes) - len(matched_gt)
 
    return tp, fp, fn
 
 
def load_baseline_boxes(baseline_csv_path):
    """
    Builds {frame_number: [[x1,y1,x2,y2], ...]} from a baseline results CSV
    produced by this same script, for use as pseudo-ground-truth.
    """
    baseline = {}
    with open(baseline_csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["class_name"] == "no_detection" or row["x1"] == "":
                continue
            frame = int(row["frame"])
            box = [int(row["x1"]), int(row["y1"]), int(row["x2"]), int(row["y2"])]
            baseline.setdefault(frame, []).append(box)
    return baseline
 
 
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Path to input video")
    parser.add_argument("--condition", required=True, help="e.g. baseline, fog, snow, dark")
    parser.add_argument("--severity", default="", help="Optional severity label, e.g. 3")
    parser.add_argument("--model", default="yolo11l.pt")
    parser.add_argument("--out", default=None, help="Output CSV path")
    parser.add_argument("--gt", default=None, help="Path to ground-truth JSON (real GT mode)")
    parser.add_argument("--baseline_csv", default=None,
                         help="Path to baseline CSV to use as pseudo-GT (proxy mode)")
    parser.add_argument("--conf", type=float, default=0.5, help="YOLO confidence threshold")
    parser.add_argument("--iou_thresh", type=float, default=0.5, help="IoU threshold for matching")
    parser.add_argument("--show", action="store_true", help="Display video while processing")
    args = parser.parse_args()
 
    mode = "none"
    gt_data = None
 
    if args.gt:
        mode = "ground_truth"
        with open(args.gt, "r") as f:
            gt_data = json.load(f)
        print(f"[INFO] Running in GROUND-TRUTH mode using {args.gt}")
    elif args.baseline_csv:
        mode = "proxy"
        gt_data = load_baseline_boxes(args.baseline_csv)
        print(f"[INFO] Running in PROXY mode (baseline-comparison, NOT true accuracy) "
              f"using {args.baseline_csv}")
    else:
        print("[INFO] No --gt or --baseline_csv provided. "
              "Only raw detection counts / confidence will be logged.")
 
    out_path = args.out or f"results_{args.condition}{('_s' + args.severity) if args.severity else ''}.csv"
 
    model = YOLO(args.model)
    cap = cv2.VideoCapture(args.video)
 
    if not cap.isOpened():
        print("Error opening video")
        return
 
    csv_file = open(out_path, mode="w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "frame", "condition", "severity", "track_id", "class_name",
        "confidence", "x1", "y1", "x2", "y2",
        "tp", "fp", "fn", "eval_mode"
    ])
 
    frame_number = 0
    totals = {"tp": 0, "fp": 0, "fn": 0, "detections": 0, "conf_sum": 0.0, "scored_frames": 0}
 
    while True:
        ret, frame = cap.read()
        if not ret:
            break
 
        frame_number += 1
 
        results = model.track(frame, persist=True, classes=[0], conf=args.conf, verbose=False)
 
        pred_boxes = []
        rows_this_frame = []
 
        has_dets = (
            results[0].boxes is not None
            and results[0].boxes.id is not None
            and len(results[0].boxes) > 0
        )
 
        if has_dets:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            class_indices = results[0].boxes.cls.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu().numpy()
 
            for box, track_id, class_idx, conf in zip(boxes, track_ids, class_indices, confidences):
                x1, y1, x2, y2 = map(int, box)
                class_name = model.names[class_idx]
                pred_boxes.append([x1, y1, x2, y2])
                totals["detections"] += 1
                totals["conf_sum"] += float(conf)
 
                if args.show:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"ID:{track_id} {class_name} {conf:.2f}",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
 
                rows_this_frame.append([
                    frame_number, args.condition, args.severity, track_id,
                    class_name, round(float(conf), 4), x1, y1, x2, y2
                ])
 
        # --- scoring against GT / pseudo-GT, if available for this frame ---
        tp = fp = fn = ""
        gt_key = str(frame_number - 1)  # adjust if your GT is 0-indexed vs 1-indexed
        if gt_data is not None and gt_key in gt_data:
            gt_boxes = gt_data[gt_key]
            tp, fp, fn = match_boxes(pred_boxes, gt_boxes, args.iou_thresh)
            totals["tp"] += tp
            totals["fp"] += fp
            totals["fn"] += fn
            totals["scored_frames"] += 1
 
        if rows_this_frame:
            for row in rows_this_frame:
                csv_writer.writerow(row + [tp, fp, fn, mode])
        else:
            # log the "no detection" frame explicitly -- important for FN tracking
            csv_writer.writerow([
                frame_number, args.condition, args.severity, None,
                "no_detection", None, None, None, None, None,
                tp, fp, fn, mode
            ])
 
        if args.show:
            cv2.imshow("YOLO Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
 
    cap.release()
    csv_file.close()
    if args.show:
        cv2.destroyAllWindows()
 
    # --- summary ---
    print("\n=== SUMMARY ===")
    print(f"Condition: {args.condition} (severity: {args.severity or 'n/a'})")
    print(f"Total frames processed: {frame_number}")
    print(f"Total detections: {totals['detections']}")
    if totals["detections"] > 0:
        print(f"Average confidence: {totals['conf_sum'] / totals['detections']:.4f}")
 
    if totals["scored_frames"] > 0:
        tp, fp, fn = totals["tp"], totals["fp"], totals["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
 
        label = "TRUE ACCURACY" if mode == "ground_truth" else "PROXY (relative to clean baseline)"
        print(f"\n[{label}]")
        print(f"Scored frames: {totals['scored_frames']}")
        print(f"TP: {tp}  FP: {fp}  FN: {fn}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall (miss rate = {1 - recall:.4f}): {recall:.4f}")
        print(f"F1: {f1:.4f}")
 
    print(f"\nResults saved to: {out_path}")
 
 
if __name__ == "__main__":
    main()