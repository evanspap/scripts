#!/bin/bash

###############################################################################
# Command Logger Script
# Logs every shell command with timestamp and working directory to a custom file.
# Coexists safely with other PROMPT_COMMAND loggers (e.g. .bashrc-based).
#
# Metadata:
#   Version : 1.1.0
#   Updated : 2026-02-22
#   Author  : Codex (updated for user request)
#
# Usage:
#   source command_logger.sh --start [logfile]   # Start logging (optional logfile)
#   source command_logger.sh --stop              # Stop logging (removes only this logger)
#
# Example:
#   source ./command_logger.sh --start ~/mylog.txt
#
# NOTE: Must be *sourced*, not executed, to affect current shell environment.
# Auto-start (Linux / WSL Bash):
#   Add one of the following lines to ~/.bashrc so logging starts automatically
#   when you open a new terminal:
#     source /full/path/to/command_logger.sh --start
#     source /full/path/to/command_logger.sh --start ~/command_log.txt
#
#   Example for this repo in WSL (adjust path as needed):
#     source "/mnt/h/My Drive/VSCode_Github/scripts/Bash/command_logger.sh" --start
#
#   Then reload Bash:
#     source ~/.bashrc
#
# Logged fields (per command):
#   timestamp     : Command timestamp (dd/mm/yy HH:MM:SS)
#   cwd           : Current working directory
#   cmd           : Command captured from shell history
#   py_env        : Active Python environment (conda / venv / pyenv / none)
#   py_bin        : Resolved python executable path (python or python3)
#   host          : Current hostname (login node or compute node)
#   ssh_from      : Remote client IP (if shell was opened via SSH)
#   ssh_to        : Server IP for SSH session (if available)
#   scheduler     : Detected HPC scheduler (slurm/pbs/lsf/sge/none)
#   cluster       : Cluster name when exposed by environment variables
#   job_id        : Scheduler job id when in a job shell
#   submit_host   : Submit/login host when available from scheduler variables
#   compute_node  : Node executing the job (or current host in some schedulers)
#
# HPC notes:
#   - On a login node (interactive SSH): host=<login-node>, scheduler=none
#   - Inside a scheduler job shell: job_id and compute_node should be populated
###############################################################################

# Default logfile
DEFAULT_LOGFILE=~/command_log.txt
LOGFILE="$2"

if [ -z "$LOGFILE" ]; then
    LOGFILE="$DEFAULT_LOGFILE"
fi

# Define our logger function
_command_logger_python_env() {
  if [ -n "$CONDA_DEFAULT_ENV" ]; then
    printf "conda:%s" "$CONDA_DEFAULT_ENV"
    return
  fi

  if [ -n "$VIRTUAL_ENV" ]; then
    printf "venv:%s" "${VIRTUAL_ENV##*/}"
    return
  fi

  if [ -n "$PYENV_VERSION" ]; then
    printf "pyenv:%s" "$PYENV_VERSION"
    return
  fi

  printf "none"
}

_command_logger_hpc_context() {
  local host ssh_from ssh_to scheduler cluster compute_node job_id submit_host

  host=$(hostname 2>/dev/null || echo "unknown")
  ssh_from="none"
  ssh_to="none"

  if [ -n "$SSH_CONNECTION" ]; then
    # SSH_CONNECTION="client_ip client_port server_ip server_port"
    ssh_from=$(printf "%s" "$SSH_CONNECTION" | awk '{print $1}')
    ssh_to=$(printf "%s" "$SSH_CONNECTION" | awk '{print $3}')
  elif [ -n "$SSH_CLIENT" ]; then
    ssh_from=$(printf "%s" "$SSH_CLIENT" | awk '{print $1}')
  fi

  scheduler="none"
  cluster="${SLURM_CLUSTER_NAME:-${CLUSTER_NAME:-}}"
  compute_node=""
  job_id=""
  submit_host=""

  if [ -n "$SLURM_JOB_ID" ]; then
    scheduler="slurm"
    job_id="$SLURM_JOB_ID"
    compute_node="${SLURMD_NODENAME:-${SLURM_NODELIST:-}}"
    submit_host="${SLURM_SUBMIT_HOST:-}"
  elif [ -n "$PBS_JOBID" ]; then
    scheduler="pbs"
    job_id="$PBS_JOBID"
    compute_node="${HOSTNAME:-$host}"
    submit_host="${PBS_O_HOST:-}"
  elif [ -n "$LSB_JOBID" ]; then
    scheduler="lsf"
    job_id="$LSB_JOBID"
    compute_node="${HOSTNAME:-$host}"
    submit_host="${LS_SUBCWD_HOST:-}"
  elif [ -n "$JOB_ID" ] && [ -n "$SGE_ROOT" ]; then
    scheduler="sge"
    job_id="$JOB_ID"
    compute_node="${HOSTNAME:-$host}"
    submit_host="${SGE_O_HOST:-}"
  fi

  printf "host=%s ssh_from=%s ssh_to=%s scheduler=%s cluster=%s job_id=%s submit_host=%s compute_node=%s" \
    "$host" \
    "$ssh_from" \
    "$ssh_to" \
    "$scheduler" \
    "${cluster:-none}" \
    "${job_id:-none}" \
    "${submit_host:-none}" \
    "${compute_node:-none}"
}

log_custom() {
  local cmd py_env py_bin
  cmd=$(history 1)
  py_env=$(_command_logger_python_env)
  py_bin=$(command -v python 2>/dev/null || command -v python3 2>/dev/null || echo "none")

  printf "%s  cwd=%s  cmd=%s  py_env=%s  py_bin=%s  %s\n" \
    "$(date +"%d/%m/%y %T")" \
    "$(pwd)" \
    "${cmd#* }" \
    "$py_env" \
    "$py_bin" \
    "$(_command_logger_hpc_context)" >> "$LOGFILE"
}

if [ "$1" == "--start" ]; then
    export HISTTIMEFORMAT="%d/%m/%y %T "

    # Only add if not already present
    case "$PROMPT_COMMAND" in
      *log_custom*) : ;;  # already added
      *) PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }log_custom" ;;
    esac

    echo "Command logging started. Appending to: $LOGFILE"

elif [ "$1" == "--stop" ]; then
    # Remove log_custom from PROMPT_COMMAND only
    PROMPT_COMMAND=$(echo "$PROMPT_COMMAND" | sed 's/;\? *log_custom\b//g')
    echo "Command logging stopped (only this logger)."

else
    echo "Command Logger"
    echo "Logs each shell command with timestamp, directory, Python env, and HPC context."
    echo "Version: 1.1.0 | Updated: 2026-02-22"
    echo
    echo "Usage:"
    echo "  source $0 --start [logfile]    # Start logging (optional logfile)"
    echo "  source $0 --stop               # Stop this logger only"
    echo
    echo "Auto-start on Linux/WSL (Bash):"
    echo "  Add to ~/.bashrc:"
    echo "    source /full/path/to/command_logger.sh --start [logfile]"
    echo "  Then run: source ~/.bashrc"
    echo
    echo "Logged metadata includes:"
    echo "  py_env / py_bin  |  host / ssh_from / ssh_to  |  scheduler/job/node fields"
    echo
    echo "NOTE: Run this script with 'source' or '.' so it affects your current shell."
    echo "Example:"
    echo "  source ./command_logger.sh --start ~/mylog.txt"
fi
