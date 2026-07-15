import cv2
from imagecorruptions import corrupt

# -----------------------
# Input and Output Videos
# -----------------------
input_video = r"C:\Users\prana\Downloads\original_video.mp4"
output_video = r"C:\Users\prana\OneDrive\Pictures\Opencv\jaad_video_fog.mp4"

cap = cv2.VideoCapture(input_video)

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(
    output_video,
    fourcc,
    fps,
    (width, height)
)

# -----------------------
# Process Video
# -----------------------
while True:
    ret, frame = cap.read()

    if not ret:
        break

    fog_frame = corrupt(
        frame,
        corruption_name="fog",
        severity=3
    )

    out.write(fog_frame)

    cv2.imshow("Fog Video", fog_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("Fog video saved.")