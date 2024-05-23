import subprocess

from typing import List


class RVCService:

    def __init__(self, logs_dir: str):
        self.logs_dir = logs_dir

    @staticmethod
    def run_model_learning(transpose_value, input_path, output_path, model_path, index_file_path, inference_device,
                           method):
        command = [
            "python", "infer_cli.py",
            str(transpose_value),
            str(input_path),
            str(output_path),
            str(model_path),
            str(index_file_path),
            str(inference_device),
            str(method)
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Finished with error {stderr.decode()}")
        else:
            print(f"Finished success: {stdout.decode()}")

    @staticmethod
    def run_command(command: List[str]):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Finished with error {stderr.decode()}")
        else:
            print(f"Finished success: {stdout.decode()}")

    def prepare_source(self, source_dir: str, model_name: str, freq: int = 40000, cores_count: int = 6,
                       noparallel=False):
        command = [
            "python3",
            "trainset_preprocess_pipeline_print.py",
            source_dir,
            freq, cores_count, self.logs_dir + model_name, noparallel
        ]

        return self.run_command(command)

    def extract_f0(self, model_name: str):
        command = [
            "python3",
            "extract_f0_print.py",
            self.logs_dir + model_name,

        ]


if __name__ == '__main__':
    rvc_service = RVCService(logs_dir="/Users/maxim/PycharmProjects/voice_emulation/logs/")





# python3.8 trainset_preprocess_pipeline_print.py "/home/u57376/voice_sources/mellstroy2/" 40000 4 "/home/u57376/voice_project/RVC_new/logs/mi-test" False


# компнда предтренировки источника python3 trainset_preprocess_pipeline_print.py "/Users/maxim/PycharmProjects/voice_emulation/voice_source/sobchak" 40000 6 "/Users/maxim/PycharmProjects/voice_emulation/logs/mi-test" False


# вытаскивание черт:   python3 extract_f0_print.py "/Users/maxim/PycharmProjects/voice_emulation/logs/mi-test" 6 pm