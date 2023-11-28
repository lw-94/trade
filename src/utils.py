import os


def write_file(file_path, content):
    directory = os.path.dirname(file_path)
    # 创建目录（如果它们不存在）
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, "w") as file:
        file.write(content)
