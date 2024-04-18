import speedtest
import time
import sys
import threading

def measure_speed(results):
    """ネットワーク速度を測定する関数"""
    st = speedtest.Speedtest()
    results['download'] = st.download()
    results['upload'] = st.upload()

def display_network_speed():
    """ネットワーク速度を測定し、結果を表示する"""
    red_start = "\033[91m"
    red_end = "\033[0m"
    print(red_start + "計測中.........." + red_end, end="")
    sys.stdout.flush()
    animation = ".........."
    results = {}

    # スピードテストを別スレッドで実行
    speed_thread = threading.Thread(target=measure_speed, args=(results,))
    speed_thread.start()

    while speed_thread.is_alive():
        for i in range(len(animation)):
            if not speed_thread.is_alive():
                break
            time.sleep(0.15)
            sys.stdout.write(red_start + "\r計測中" + animation[:i] + '/' + animation[i+1:] + red_end)
            sys.stdout.flush()

    # 計測結果の表示
    download_speed = results['download']
    upload_speed = results['upload']
    print(red_start + f"\rダウンロード速度: {download_speed/1024/1024:.2f} Mbps, アップロード速度: {upload_speed/1024/1024:.2f} Mbps" + red_end)
