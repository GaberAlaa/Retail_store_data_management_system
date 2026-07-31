import json
from Modules import config 


def get_log_path():
    config.LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    log_path = config.LOGS_FOLDER / "log.json"
    if not log_path.exists():
        log_path.write_text("[]")
    return log_path


def read_log(log_path):
    with open(log_path) as f:
        return json.load(f)


def has_been_logged(log_data, file_name):
    return any(entry["file"] == file_name for entry in log_data)


def add_log_entry(log_data, file_name, status, issues):
    log_data.append({
        "file": file_name,
        "status": status,
        "issues": issues,
    })
    return log_data


def write_log(log_path, log_data):
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)


def generate_log_file(status, file_path, issues):

    log_path = get_log_path()
    log_data = read_log(log_path)

    file_name = file_path.name

    if not has_been_logged(log_data, file_name):
        log_data = add_log_entry(log_data, file_name, status, issues)
        write_log(log_path, log_data)

    return log_path