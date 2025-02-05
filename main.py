import cv2
import time
from ultralytics import YOLO
import paramiko
import threading

def play_rtsp(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        return

    frame_count = 0
    start_time = time.time()
    model = YOLO('yolo11n-pose.pt')  # YOLOv8 Poseモデルの読み込み

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, stream=False, batch=10, imgsz=320, conf=0.85)  # フレームに対して推論を実行

        # 結果をフレームに描画
        frame = results[0].plot(conf=0.9)

        frame_count += 1
        elapsed_time = time.time() - start_time

        if elapsed_time > 0:
            fps = frame_count / elapsed_time
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('RTSPストリーム', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def execute_ssh_command(host, port, username, password, command):
    try:
        # SSHクライアントの作成
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # SSHサーバーに接続
        client.connect(host, port=port, username=username, password=password)
        
        # コマンドの実行
        stdin, stdout, stderr = client.exec_command(command)
        
        # 結果の取得
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        # 接続のクローズ
        client.close()
        
        return output, error
    except Exception as e:
        return None, str(e)

def run_ssh_command():
    host = "darts"
    port = 22
    username = "darts"
    password = "darts#3"
    command = "/usr/bin/libcamera-vid -t 0 --inline -o - --level 4.2 --denoise cdn_off --framerate 60 --width 1280 --height 720 | /usr/bin/cvlc stream:///dev/stdin --sout='#rtp{sdp=rtsp://:8554/stream1}' :demux=h264 --preferred-resolution 1080"
    output, error = execute_ssh_command(host, port, username, password, command)
    if output:
        print("Output:", output)
    if error:
        print("Error:", error)

if __name__ == '__main__': # pragma: no covers
    ssh_thread = threading.Thread(target=run_ssh_command)
    ssh_thread.start()
    play_rtsp("rtsp://darts:8554/stream1")
