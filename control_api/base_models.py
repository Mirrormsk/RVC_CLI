from pydantic import BaseModel


class TaskType(BaseModel):
    name: str
    command: str


class Task(BaseModel):
    type: TaskType
    s3_file_url: str
    model_name: str


# python infer_cli.py [TRANSPOSE_VALUE] "[INPUT_PATH]" "[OUTPUT_PATH]" "[MODEL_PATH]" "[INDEX_FILE_PATH]" "[INFERENCE_DEVICE]" "[METHOD]"

