import csv
import datetime
import glob
import json
import logging
import os
import shutil


def post_analysis_fluviewer_nf(config, pipeline, run):
    """
    Perform post-analysis tasks for the fluviewer-nf pipeline.

    :param config: The config dictionary
    :type config: dict
    :param pipeline: The pipeline dictionary
    :type pipeline: dict
    :param run: The run dictionary
    :type run: dict
    :return: None
    :rtype: None
    """
    logging.info(json.dumps({
        "event_type": "post_analysis_started",
        "sequencing_run_id": run['sequencing_run_id'],
        "pipeline": pipeline,
        "run": run,
    }))
    sequencing_run_id = run['sequencing_run_id']
    analysis_run_output_dir = os.path.join(config['analysis_output_dir'], sequencing_run_id)

    return None

pipeline_post_analysis_functions = {
    'BCCDC-PHL/fluviewer-nf': post_analysis_fluviewer_nf,
}

def post_analysis(config, pipeline, run):
    """
    Perform post-analysis tasks for a pipeline.

    :param config: The config dictionary
    :type config: dict
    :param pipeline: The pipeline dictionary
    :type pipeline: dict
    :param run: The run dictionary
    :type run: dict
    :return: None
    """
    pipeline_name = pipeline['pipeline_name']
    pipeline_short_name = pipeline_name.split('/')[1]
    pipeline_version = pipeline['pipeline_version']
    delete_pipeline_work_dir = pipeline.get('delete_work_dir', True)
    sequencing_run_id = run['sequencing_run_id']
    base_analysis_work_dir = config['analysis_work_dir']

    # The work_dir includes a timestamp, so we need to glob to find the most recent one
    work_dir_glob = os.path.join(base_analysis_work_dir, 'work-' + sequencing_run_id + '_' + pipeline_short_name + '_' + '*')
    work_dirs = glob.glob(work_dir_glob)
    if len(work_dirs) > 0:
        work_dir = work_dirs[-1]
    else:
        work_dir = None

    if work_dir and delete_pipeline_work_dir:
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
            logging.info(json.dumps({
                "event_type": "analysis_work_dir_deleted",
                "sequencing_run_id": sequencing_run_id,
                "analysis_work_dir_path": work_dir
            }))
        except OSError as e:
            logging.error(json.dumps({
                "event_type": "delete_analysis_work_dir_failed",
                "sequencing_run_id": sequencing_run_id,
                "analysis_work_dir_path": work_dir
            }))
    else:
        if not work_dir or not os.path.exists(work_dir):
            logging.warning(json.dumps({
                "event_type": "analysis_work_dir_not_found",
                "sequencing_run_id": sequencing_run_id,
                "analysis_work_dir_glob": work_dir_glob
            }))
        elif not delete_pipeline_work_dir:
            logging.info(json.dumps({
                "event_type": "skipped_deletion_of_analysis_work_dir",
                "sequencing_run_id": sequencing_run_id,
                "analysis_work_dir_path": work_dir
            }))

    if pipeline_name in pipeline_post_analysis_functions:
        return pipeline_post_analysis_functions[pipeline_name](config, pipeline, run)
    else:
        logging.warning(json.dumps({
            "event_type": "post_analysis_not_implemented",
            "sequencing_run_id": sequencing_run_id,
            "pipeline_name": pipeline_name
        }))
        return None