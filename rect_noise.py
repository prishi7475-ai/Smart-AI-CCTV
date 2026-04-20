import cv2

donel = False
doner = False
x1, y1, x2, y2 = 0, 0, 0, 0

def select(event, x, y, flags, param):
    global x1, y1, x2, y2, donel, doner
    if event == cv2.EVENT_LBUTTONDOWN:
        x1, y1 = x, y
        donel = True
    elif event == cv2.EVENT_RBUTTONDOWN:
        x2, y2 = x, y
        doner = True
        print(f"Selected from ({x1}, {y1}) to ({x2}, {y2})")

def rect_noise():
    global x1, y1, x2, y2, donel, doner
    donel = doner = False  # Reset selection flags

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot access camera.")
        return

    cv2.namedWindow("Select Region")
    cv2.setMouseCallback("Select Region", select)

    print("Select region: Left-click to start, Right-click to end.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame.")
            break

        cv2.imshow("Select Region", frame)

        if cv2.waitKey(1) == 27 or (donel and doner):
            break

    cv2.destroyWindow("Select Region")

    # Normalize coordinates (handle reverse drag)
    x_start, x_end = min(x1, x2), max(x1, x2)
    y_start, y_end = min(y1, y2), max(y1, y2)

    print(f"Monitoring region from ({x_start}, {y_start}) to ({x_end}, {y_end})")

    while True:
        ret1, frame1 = cap.read()
        ret2, frame2 = cap.read()
        if not (ret1 and ret2):
            print("Error: Failed to read frames.")
            break

        roi1 = frame1[y_start:y_end, x_start:x_end]
        roi2 = frame2[y_start:y_end, x_start:x_end]

        if roi1.size == 0 or roi2.size == 0:
            print("Error: Selected region is invalid.")
            break

        diff = cv2.absdiff(roi2, roi1)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        diff = cv2.blur(diff, (5, 5))
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            max_cnt = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_cnt)
            cv2.rectangle(frame1, (x + x_start, y + y_start), (x + x_start + w, y + y_start + h), (0, 255, 0), 2)
            cv2.putText(frame1, "MOTION", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
        else:
            cv2.putText(frame1, "NO-MOTION", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

        # Draw selected region box
        cv2.rectangle(frame1, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)
        cv2.imshow("Motion in Region (ESC to exit)", frame1)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
