import datetime
import json
import logging
import os
import shutil
import subprocess


def build_pipeline_command(config, pipeline):
    """
    Builds the pipeline command to be executed.

    :param config: The config dictionary
    :type config: dict
    :param pipeline: The pipeline dictionary
    :type pipeline: dict
    :return: The pipeline command to be executed, as a list of strings
    :rtype: list
    """

    pipeline_command = [
            'nextflow',
            '-log', pipeline['pipeline_parameters']['log_path'],
            'run',
            pipeline['pipeline_name'],
            '-r', pipeline['pipeline_version'],
            '-profile', 'conda',
            '--cache', os.path.join(os.path.expanduser('~'), '.conda/envs'),
            '-work-dir', pipeline['pipeline_parameters']['work_dir'],
            '-with-report', pipeline['pipeline_parameters']['report_path'],
            '-with-trace', pipeline['pipeline_parameters']['trace_path'],
            '-with-timeline', pipeline['pipeline_parameters']['timeline_path'],
    ]
    pipeline['pipeline_parameters'].pop('log_path', None)
    pipeline['pipeline_parameters'].pop('report_path', None)
    pipeline['pipeline_parameters'].pop('trace_path', None)
    pipeline['pipeline_parameters'].pop('timeline_path', None)

    for flag, value in pipeline['pipeline_parameters'].items():
        if value is None:
            pipeline_command += ['--' + flag]
        else:
            pipeline_command += ['--' + flag, value]
    
    return pipeline_command


def run_pipeline(config, pipeline, run):
    """
    Analyzes a run.

    :param config: The config dictionary
    :type config: dict
    :param run: The run dictionary
    :type run: dict
    :param pipeline: The pipeline dictionary
    :type pipeline: dict
    :return: None
    :rtype: None
    """

    analysis_tracking = {
        "timestamp_analysis_start": datetime.datetime.now().isoformat()
    }
    pipeline_command = build_pipeline_command(config, pipeline)
    pipeline_command_str = list(map(str, pipeline_command))

    sequencing_run_id = run['sequencing_run_id']
    analysis_work_dir = pipeline['pipeline_parameters']['work_dir']

    try:
        os.makedirs(analysis_work_dir)
        logging.info(json.dumps({
            "event_type": "analysis_started",
            "sequencing_run_id": sequencing_run_id,
            "pipeline_command": pipeline_command_str
        }))
        analysis_result = subprocess.run(pipeline_command_str, capture_output=True, check=True, cwd=analysis_work_dir)
        analysis_tracking["timestamp_analysis_complete"] = datetime.datetime.now().isoformat()
        analysis_complete_path = os.path.join(pipeline['pipeline_parameters']['outdir'], 'analysis_complete.json')
        with open(analysis_complete_path, 'w') as f:
                json.dump(analysis_tracking, f, indent=2)
                f.write('\n')
        logging.info(json.dumps({
            "event_type": "analysis_complete",
            "sequencing_run_id": sequencing_run_id,
            "pipeline_command": pipeline_command_str,
        }))
    except subprocess.CalledProcessError as e:
        logging.error(json.dumps({
            "event_type": "analysis_failed",
            "sequencing_run_id": sequencing_run_id,
            "pipeline_command": pipeline_command_str,
            "error": str(e)
        }))