# auto-flu
Automated analysis of flu sequence data using the [BCCDC-PHL/FluViewer_nf](https://github.com/BCCDC-PHL/FluViewer_nf) pipeline.

# Installation

# Usage
Start the tool as follows:

```bash
auto-flu --config config.json
```

See the Configuration section of this document for details on preparing a configuration file.

More detailed logs can be produced by controlling the log level using the `--log-level` flag:

```bash
auto-flu --config config.json --log-level debug
```

# Configuration
This tool takes a single config file, in JSON format, with the following structure:

```json
{
  "fastq_by_run_dir": "/path/to/fastq_symlinks_by_run",
  "analysis_output_dir": "/path/to/analysis_by_run",
  "analysis_work_dir": "/path/to/auto-flu-work",
  "notification_email": "someone@example.org",
  "send_notification_emails": true,
  "scan_interval_seconds": 3600,
  "pipelines": [
    {
      "pipeline_name": "BCCDC-PHL/FluViewer_nf",
      "pipeline_version": "0.0.9",
      "pipeline_parameters": {
  	    "fastq_input": null,
   	    "db": "/path/to/FluViewer_db.fa",
   	    "outdir": null
      }
	}
  ]
}
```
