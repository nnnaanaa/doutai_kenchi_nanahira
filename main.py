import requests
import json
import io
import wave
import pyaudio
import time
import cv2
import threading

def main():
    inst = MotionDetection()
    inst.motion_detection()

class VoicevoxEngine:
    def __init__(self,host="127.0.0.1",port=50021):
        self.host = host
        self.port = port

    def speak(self,text=None,speaker=54): # spaker_id = ななひら
        params = (
            ("text", text),
            ("speaker", speaker)
        )

        try:
            init_q = requests.post(
                f"http://{self.host}:{self.port}/audio_query",
                params=params
            )

            res = requests.post(
                f"http://{self.host}:{self.port}/synthesis",
                headers={"Content-Type": "application/json"},
                params=params,
                data=json.dumps(init_q.json())
            )
        # http request error
        except requests.exceptions.RequestException as e:
            print(e)
            return False

        # メモリ展開
        audio = io.BytesIO(res.content)

        with wave.open(audio,'rb') as f:
            # 音声再生処理
            p = pyaudio.PyAudio()

            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                return (data, pyaudio.paContinue)

            stream = p.open(format=p.get_format_from_width(width=f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True,
                            stream_callback=_callback)

            # 音声再生
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            p.terminate()

# 非同期実行にしないと後続処理が実行できない。
class MotionDetection:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.voicevox_engine = VoicevoxEngine()

    def kimi_no_say(self):
        # threadingの動作を見る
        time.sleep(10)
        print("kimi_no_say")

    def motion_detection(self):
        before = None

        while True:
            #  OpenCVでWebカメラの画像を取り込む
            ret, frame = self.cap.read()

            # スクリーンショットを撮りたい関係で1/4サイズに縮小
            frame = cv2.resize(frame, (int(frame.shape[1]), int(frame.shape[0])))
            # 加工なし画像を表示する(表示しない)
            # cv2.imshow('Raw Frame', frame)

            # 取り込んだフレームに対して差分をとって動いているところが明るい画像を作る
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if before is None:
                before = gray.copy().astype('float')
                continue
            # 現フレームと前フレームの加重平均を使うと良いらしい
            cv2.accumulateWeighted(gray, before, 0.5)
            mdframe = cv2.absdiff(gray, cv2.convertScaleAbs(before))
            # 動いているところが明るい画像を表示する(表示しない)
            # cv2.imshow('MotionDetected Frame', mdframe)

            # 動いているエリアの面積を計算してちょうどいい検出結果を抽出する
            thresh = cv2.threshold(mdframe, 3, 255, cv2.THRESH_BINARY)[1]
            # 輪郭データに変換しくれるfindContours
            contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #この行
            max_area = 0
            try:
                target = contours[0]
            except IndexError:
                continue
            for cnt in contours:
                #輪郭の面積を求めてくれるcontourArea
                area = cv2.contourArea(cnt)
                if max_area < area and area < 10000 and area > 1000:
                    max_area = area
                    target = cnt

            # 動いているエリアのうちそこそこの大きさのものがあればそれを矩形で表示する
            if max_area <= 1000:
                areaframe = frame
                cv2.putText(areaframe, 'not detected', (0,50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255,0), 3, cv2.LINE_AA)
            else:
                # 動体検知あり→イベント
                # 諸般の事情で矩形検出とした。
                
                # voicevox起動(非同期実行)
                text = "動体を検知しました。"
                t1 = threading.Thread(target = self.voicevox_engine.speak(text))
                t1.start()

                x,y,w,h = cv2.boundingRect(target)
                areaframe = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

            cv2.imshow('MotionDetected Area Frame', areaframe)
            # キー入力を1ms待って、k が27（ESC）だったらBreakする
            k = cv2.waitKey(1)
            if k == 27:
                t1.join()
                break

        # キャプチャをリリースして、ウィンドウをすべて閉じる
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
