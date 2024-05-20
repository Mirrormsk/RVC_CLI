import subprocess
import logging
import json

import botocore
import requests
import os
from typing import List
import fcntl

from aws import AWSService
from config import settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class RVCService:
    def __init__(
        self, source_save_path: str, results_path: str, logs_dir: str = "logs"
    ):
        self.results_path = results_path
        self.source_save_path = source_save_path
        self.files_for_process_dir = "files"
        self.logs_dir = logs_dir
        self.batch_size = settings.batch_size
        self.data_file = "models.json"
        self.callback_url = settings.callback_url
        self.requests_retry = 5
        self.python_command = "python"
        self.main_py_path = "main.py"
        self.s3_results_path = "received_from_rvc"

        for path in (
            self.files_for_process_dir,
            self.source_save_path,
            self.results_path,
        ):
            if not os.path.exists(path):
                os.makedirs(path)

        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as file:
                json.dump({}, file)

    def add_model_info(
        self, model_name: str, pth_path: str = None, index_path: str = None
    ):
        """Insert model info in json file"""
        print(f"Adding model info for {model_name}")

        try:
            with open(self.data_file, "r+") as file:
                fcntl.flock(file, fcntl.LOCK_EX)

                try:
                    data = json.load(file)
                except (json.JSONDecodeError, FileNotFoundError):
                    data = {}

                model_data = data.get(model_name, dict())

                if pth_path is not None:
                    model_data["pth_path"] = pth_path

                if index_path is not None:
                    model_data["index_path"] = index_path

                data[model_name] = model_data

                file.seek(0)
                file.truncate()

                json.dump(data, file, indent=4)

        except IOError as e:
            logger.error(f"Error while try write data to json file: {e}")

    def get_model_data(self, model_name: str):
        """Returns model info dict"""
        try:
            with open(self.data_file, "r") as file:
                fcntl.flock(file, fcntl.LOCK_SH)

                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    return None

                return data.get(model_name, None)
        except IOError as e:
            logger.error(f"Error while try to read data from json file: {e}")
            return None

    def send_callback_data(self, data: dict) -> None:
        """Send data to server"""

        for _ in range(self.requests_retry):
            try:
                response = requests.post(
                    url=self.callback_url,
                    data=data,
                )
            except requests.exceptions.RequestException as ex:
                logger.error(f"Error while sending callback: {ex}", exc_info=True)
            else:
                logger.debug(f"Response from server: {response.json()}")
                if response.status_code == 200:
                    break

    def download_model(
        self, model_name: str, pth_file_s3_path: str, index_file_s3_path: str
    ):

        pth_save_dir = self.logs_dir
        index_save_dir = os.path.join(self.logs_dir, model_name)

        pth_save_path = os.path.join(pth_save_dir, pth_file_s3_path.split("/")[-1])
        index_save_path = os.path.join(
            index_save_dir, index_file_s3_path.split("/")[-1]
        )

        if not os.path.exists(index_save_dir):
            os.makedirs(index_save_dir)
        try:
            AWSService.download_file(pth_file_s3_path, pth_save_path)
            AWSService.download_file(index_file_s3_path, index_save_path)
        except IOError as e:
            logger.error(f"IO error while download model: {e}", exc_info=True)
        except Exception as ex:
            logger.error(f"Error while download model: {ex}", exc_info=True)
        else:
            rvc_service.add_model_info(
                model_name=model_name,
                pth_path=pth_save_path,
                index_path=index_save_path,
            )
            logger.info(f"Successfully downloaded model data: {model_name}")

    def send_model_info(
        self, model_name: str, model_status: str = None, current_epoch: int = None
    ) -> None:
        """Send model status to server"""

        data = {
            "event_type": "update_model_info",
            "model_name": model_name,
            "model_status": model_status,
            "current_epoch": current_epoch,
        }

        self.send_callback_data(data)

    def send_convert_result(self, file_id: int, s3_path: str):
        """Send converted result to server"""

        data = {
            "event_type": "save_result",
            "file_id": file_id,
            "s3_path": s3_path,
        }
        self.send_callback_data(data)

    def retrieve_command(self, command_data: dict):
        """Retrieve command from ampq"""
        if "command" not in command_data:
            logger.warning(f"No command specified: {command_data}")
            return None

        command = command_data["command"]

        if command == "training":
            return self.run_training(
                model_name=command_data["model_name"],
                source_aws_url=command_data["source_aws_url"],
                total_epoch=command_data["total_epoch"],
            )
        elif command == "process":
            return self.run_infer(
                model_name=command_data["model_name"],
                file_aws_url=command_data["file_aws_url"],
                file_id=command_data["file_id"],
                pth_file_s3_path=command_data["pth_file_s3_path"],
                index_file_s3_path=command_data["index_file_s3_path"],
            )
        else:
            logger.warning(f"Unknown command: {command}")
            return None

    @staticmethod
    def _run_process(command: List[str]):
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())
        stderr = process.stderr.read()
        return_code = process.poll()

        if return_code != 0:
            print(f"Command failed with return code {return_code}")
            if stderr:
                print(f"Errors: {stderr}")

        return return_code, stderr

    def prepare_source(
        self, dataset_path: str, model_name: str, sampling_rate: int = 40000
    ):
        command = [
            self.python_command,
            self.main_py_path,
            "preprocess",
            "--model_name",
            model_name,
            "--dataset_path",
            dataset_path,
            "--sampling_rate",
            str(sampling_rate),
        ]
        return self._run_process(command)

    def run_extract_features_command(
        self,
        model_name: str,
        rvc_version: str = "v2",
        f0method: str = "rmvpe",
        hop_length: int = 128,
        sampling_rate: int = 40000,
    ):
        command = [
            self.python_command,
            self.main_py_path,
            "extract",
            "--model_name",
            model_name,
            "--rvc_version",
            rvc_version,
            "--f0method",
            f0method,
            "--hop_length",
            str(hop_length),
            "--sampling_rate",
            str(sampling_rate),
        ]
        return self._run_process(command)

    def run_start_training_command(
        self,
        model_name: str,
        batch_size: str,
        rvc_version: str = "v2",
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
        g_pretrained: str = None,
        d_pretrained: str = None,
    ):
        command = [
            self.python_command,
            self.main_py_path,
            "train",
            "--model_name",
            model_name,
            "--rvc_version",
            rvc_version,
            "--save_every_epoch",
            str(save_every_epoch),
            "--save_only_latest",
            str(save_only_latest),
            "--save_every_weights",
            str(save_every_weights),
            "--total_epoch",
            str(total_epoch),
            "--sampling_rate",
            str(sampling_rate),
            "--batch_size",
            str(batch_size),
            "--gpu",
            str(gpu),
            "--pitch_guidance",
            str(pitch_guidance),
            "--overtraining_detector",
            str(overtraining_detector),
            "--overtraining_threshold",
            str(overtraining_threshold),
            "--pretrained",
            str(pretrained),
            "--custom_pretrained",
            str(custom_pretrained),
            "--g_pretrained",
            g_pretrained or "",
            "--d_pretrained",
            d_pretrained or "",
        ]

        return self._run_process(command)

    def run_generate_index_file_command(self, model_name: str, rvc_version: str = "v2"):
        command = [
            self.python_command,
            self.main_py_path,
            "index",
            "--model_name",
            model_name,
            "--rvc_version",
            rvc_version,
        ]
        return self._run_process(command)

    def run_infer_command(
        self,
        input_path: str,
        output_path: str,
        pth_path: str,
        index_path: str,
        export_format: str = "WAV",
    ):
        command = [
            self.python_command,
            self.main_py_path,
            "infer",
            "--input_path",
            input_path,
            "--output_path",
            output_path,
            "--pth_path",
            pth_path,
            "--index_path",
            index_path,
            "--export_format",
            export_format,
        ]

        return self._run_process(command)

    def run_training(self, model_name: str, source_aws_url: str, total_epoch: int):

        self.send_model_info(model_name=model_name, model_status="IN_PROGRESS")

        dataset_save_path = os.path.join(self.source_save_path, model_name)
        filename = source_aws_url.rsplit("/", maxsplit=1)[-1]
        full_path = os.path.join(dataset_save_path, filename)

        if not os.path.exists(dataset_save_path):
            os.makedirs(dataset_save_path)

        AWSService.download_file(source_aws_url, full_path)

        print(f"Starting prepare process for model {model_name}")

        #  Prepare
        return_code, stderr = self.prepare_source(
            dataset_path=dataset_save_path,
            model_name=model_name,
        )
        print(f"Finished prepare process for model {model_name}")

        if return_code != 0:
            logger.error(f"Prepare process failed: {return_code}. Errors: {stderr}")
            return
        else:
            logger.info("Prepare process succeeded")

        # Extract features
        print(f"Starting extract features process for model {model_name}")
        return_code, stderr = self.run_extract_features_command(
            model_name=model_name,
        )

        print(f"Finished extract features process for model {model_name}")
        if return_code != 0:
            logger.error(
                f"Extract features process failed, stop execution. Errors: {stderr}"
            )
            return
        else:
            logger.info("Extract features process succeeded")

        # Start training
        return_code, stderr = self.run_start_training_command(
            model_name=model_name, batch_size=self.batch_size, total_epoch=total_epoch
        )

        if return_code != 0:
            logger.error(
                f"Start training process failed, stop execution. Errors: {stderr}"
            )
            return
        else:
            logger.info("Start training process succeeded")

        # Generate index File

        return_code, stderr = self.run_generate_index_file_command(
            model_name=model_name,
        )

        if return_code != 0:
            logger.error(
                f"Generate index process failed, stop execution. Errors: {stderr}"
            )
            return
        else:
            logger.info("Generate index process succeeded")

        logger.info(f"Training task finished! Listen for new messages")

    def run_infer(
        self,
        model_name: str,
        file_aws_url: str,
        file_id: int,
        pth_file_s3_path: str,
        index_file_s3_path: str,
    ):
        filename = file_aws_url.rsplit("/", maxsplit=1)[-1]
        full_path = os.path.join(self.files_for_process_dir, filename)

        filename_with_ext = filename.split(".")[0] + ".wav"
        output_path = os.path.join(self.results_path, filename_with_ext)
        s3_path = f"{self.s3_results_path}/{filename_with_ext}"

        print(f"Running inference on {filename_with_ext}")

        AWSService.download_file(file_aws_url, full_path)

        model_data = rvc_service.get_model_data(model_name=model_name)

        if model_data is None:
            logger.error(f"Model data not found locally: {model_name}")
            try:
                self.download_model(
                    model_name=model_name,
                    pth_file_s3_path=pth_file_s3_path,
                    index_file_s3_path=index_file_s3_path,
                )
            except Exception as ex:
                logger.error(
                    f"Error while trying to download model info: {ex}", exc_info=True
                )
                return
            else:
                model_data = rvc_service.get_model_data(model_name=model_name)

        return_code, stderr = self.run_infer_command(
            input_path=full_path,
            output_path=output_path,
            pth_path=model_data.get("pth_path"),
            index_path=model_data.get("index_path"),
        )

        if return_code != 0:
            logger.error(f"File processing failed, stop execution. Errors: {stderr}")
            return
        else:
            logger.info("File processing succeeded")
            AWSService.upload_file_to_s3(output_path, s3_path=s3_path)
            self.send_convert_result(file_id=int(file_id), s3_path=s3_path)


rvc_service = RVCService(source_save_path="sources", results_path="results")
