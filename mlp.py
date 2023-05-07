# 非同期処理の検証

import multiprocessing
import time

def x():
    time.sleep(10)
    print("Function x has finished.")

# 子プロセスは実行数分作成される
def main():
    while True:
        p = multiprocessing.Process(target=x)
        p.start()
        p.join(timeout=0.1)
        print("Continuing with next iteration.")

# 子プロセスは一つのみ生成する
def main_v2():
    while True:
        if multiprocessing.active_children() == []:
            p = multiprocessing.Process(target=x)
            p.start()
        print("Continuing with next iteration.")

if __name__ == "__main__":
    main_v2()