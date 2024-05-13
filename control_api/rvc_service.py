import subprocess

from typing import List


class RVCService:

    # def __init__(self, logs_dir: str):
    #     self.logs_dir = logs_dir

    @staticmethod
    def run_command(command: List[str]):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Finished with error {stderr.decode()}")
        else:
            print(f"Finished success: {stdout.decode()}")

    def prepare_source(self, dataset_path: str, model_name: str, sampling_rate: int = 40000, ):

        command = [
            "python",
            "main.py",
            "preprocess",
            "--model_name", model_name,
            "--dataset_path", dataset_path,
            "--sampling_rate", sampling_rate
        ]

        return self.run_command(command)

    def run_extract_features_command(self, model_name: str, rvc_version: str = 'v2', f0method: str = "rmvpe", hop_length: int = 128,
                         sampling_rate: int = 40000):
        command = [
            "python",
            "main.py",
            "extract",
            "--model_name", model_name,
            "--rvc_version", rvc_version,
            "--f0method", f0method,
            "--hop_length", hop_length,
            "--sampling_rate", sampling_rate
        ]
        return self.run_command(command)

    def run_start_training_command(self, model_name: str,
                                   batch_size: str,
                                   g_pretrained: str,
                                   d_pretrained: str,
                                   rvc_version: str = 'v2',
                                   save_every_epoch: int = 50,
                                   save_only_latest: bool = False,
                                   save_every_weights: bool = True,
                                   total_epoch: int = 1000,
                                   sampling_rate: int = 40000,
                                   gpu: int = 0,
                                   pitch_guidance: bool = True,
                                   overtraining_detector: bool = False,
                                   overtraining_threshold: int = 50,
                                   pretrained: bool = True,
                                   custom_pretrained: bool = False,

                                   ):
        command = [
            "python",
            "main.py",
            "train",
            "--model_name", model_name,
            "--rvc_version", rvc_version,
            "--save_every_epoch", save_every_epoch,
            "--save_only_latest", save_only_latest,
            "--save_every_weights", save_every_weights,
            "--total_epoch", total_epoch,
            "--sampling_rate", sampling_rate,
            "--batch_size", batch_size,
            "--gpu", gpu,
            "--pitch_guidance", pitch_guidance,
            "--overtraining_detector", overtraining_detector,
            "--overtraining_threshold", overtraining_threshold,
            "--pretrained", pretrained,
            "--custom_pretrained", custom_pretrained,
            "--g_pretrained", g_pretrained,
            "--d_pretrained", d_pretrained,

        ]

        return self.run_command(command)

    def run_generate_index_file_command(self, model_name: str, rvc_version: str = 'v2'):
        command = [
            "python",
            "main.py",
            "index",
            "--model_name", model_name,
            "--rvc_version", rvc_version,
        ]

        return self.run_command(command)


if __name__ == '__main__':
    rvc_service = RVCService()

# python3.8 trainset_preprocess_pipeline_print.py "/home/u57376/voice_sources/mellstroy2/" 40000 4 "/home/u57376/voice_project/RVC_new/logs/mi-test" False


# компнда предтренировки источника python3 trainset_preprocess_pipeline_print.py "/Users/maxim/PycharmProjects/voice_emulation/voice_source/sobchak" 40000 6 "/Users/maxim/PycharmProjects/voice_emulation/logs/mi-test" False


# вытаскивание черт:   python3 extract_f0_print.py "/Users/maxim/PycharmProjects/voice_emulation/logs/mi-test" 6 pm
