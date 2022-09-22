import json
import logging
import os
import re
import subprocess
import uuid

from typing import Iterator, Optional


def find_fastq_dirs(config, check_symlinks_complete=True):
    miseq_run_id_regex = "\d{6}_M\d{5}_\d+_\d{9}-[A-Z0-9]{5}"
    nextseq_run_id_regex = "\d{6}_VH\d{5}_\d+_[A-Z0-9]{9}"
    fastq_by_run_dir = config['fastq_by_run_dir']
    subdirs = os.scandir(fastq_by_run_dir)
    analysis_base_outdir = config['analysis_output_dir']
    for subdir in subdirs:
        run_id = subdir.name
        analysis_outdir = os.path.abspath(os.path.join(analysis_base_outdir, run_id))
        matches_miseq_regex = re.match(miseq_run_id_regex, run_id)
        matches_nextseq_regex = re.match(nextseq_run_id_regex, run_id)
        if check_symlinks_complete:
            ready_to_analyze = os.path.exists(os.path.join(subdir.path, "symlinks_complete.json"))
        else:
            ready_to_analyze = True
        analysis_not_already_initiated = not os.path.exists(analysis_outdir)
        conditions_checked = {
            "is_directory": subdir.is_dir(),
            "matches_illumina_run_id_format": ((matches_miseq_regex is not None) or (matches_nextseq_regex is not None)),
            "ready_to_analyze": ready_to_analyze,
            "analysis_not_already_initiated": analysis_not_already_initiated,
        }
        conditions_met = list(conditions_checked.values())
        pipeline_parameters = {}
        if all(conditions_met):
            logging.info(json.dumps({"event_type": "fastq_directory_found", "sequencing_run_id": run_id, "fastq_directory_path": os.path.abspath(subdir.path)}))
            pipeline_parameters['fastq_input'] = os.path.abspath(subdir.path)
            pipeline_parameters['outdir'] = analysis_outdir
            yield pipeline_parameters
        else:
            logging.debug(json.dumps({"event_type": "directory_skipped", "fastq_directory_path": os.path.abspath(subdir.path), "conditions_checked": conditions_checked}))
            yield None
    

def scan(config: dict[str, object]) -> Iterator[Optional[dict[str, object]]]:
    """
    Scanning involves looking for all existing runs and storing them to the database,
    then looking for all existing symlinks and storing them to the database.
    At the end of a scan, we should be able to determine which (if any) symlinks need to be created.

    :param config: Application config.
    :type config: dict[str, object]
    :return: A run directory to analyze, or None
    :rtype: Iterator[Optional[dict[str, object]]]
    """
    logging.info(json.dumps({"event_type": "scan_start"}))
    for symlinks_dir in find_fastq_dirs(config):    
        yield symlinks_dir


def analyze_run(config, run):
    """
    Initiate an analysis on one directory of fastq files.
    """
    base_analysis_outdir = config['analysis_output_dir']
    base_analysis_work_dir = config['analysis_work_dir']
    notification_email = config['notification_email']
    for pipeline in config['pipelines']:
        pipeline_parameters = pipeline['pipeline_parameters']
        analysis_uuid = str(uuid.uuid4())
        analysis_run_id = os.path.basename(run['fastq_input'])
        analysis_work_dir = os.path.abspath(os.path.join(base_analysis_work_dir, 'work-' + analysis_uuid))
        analysis_report_path = os.path.abspath(os.path.join(base_analysis_outdir, analysis_run_id, analysis_run_id + '_' + analysis_uuid + '_report.html'))
        analysis_trace_path = os.path.abspath(os.path.join(base_analysis_outdir, analysis_run_id, analysis_run_id + '_' + analysis_uuid + '_trace.txt'))
        analysis_timeline_path = os.path.abspath(os.path.join(base_analysis_outdir, analysis_run_id, analysis_run_id + '_' + analysis_uuid + '_timeline.html'))
        pipeline_command = [
            'nextflow',
            'run',
            pipeline['pipeline_name'],
            '-r', pipeline['pipeline_version'],
            '-profile', 'conda',
            '--cache', os.path.join(os.path.expanduser('~'), '.conda/envs'),
            '-work-dir', analysis_work_dir,
            '-with-report', analysis_report_path,
            '-with-trace', analysis_trace_path,
            '-with-timeline', analysis_timeline_path,
            '-with-notification', notification_email,
        ]
        for flag, config_value in pipeline_parameters.items():
            if config_value is None:
                value = run[flag]
            else:
                value = config_value
            pipeline_command += ['--' + flag, value]
        logging.info(json.dumps({"event_type": "analysis_started", "pipeline_command": pipeline_command}))
        tmp_pipeline_command = ['nextflow', 'run', 'hello', '-work-dir', analysis_work_dir, '-with-notification', notification_email]
        subprocess.run(pipeline_command)
