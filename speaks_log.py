import logging

def nanahira_speaks_log():
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # フォーマッターの作成
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # ファイルハンドラの作成
    file_handler = logging.FileHandler('./log/nanahira_speaks.log')
    file_handler.setFormatter(formatter)

    # ロガーにファイルハンドラを追加
    logger.addHandler(file_handler)
    return logger

if __name__ == '__main__':
    pass
