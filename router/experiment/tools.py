def read_file(file_path):
    print(file_path, "read file args")
    message = "read file executed"
    return message


def content_writer(prompt):
    print(prompt, "content_writer args")
    message = "content_writer executed"
    return message


def write_file(file_path, content):
    print(file_path, content, "write file args")
    message = "write file executed"
    return message
