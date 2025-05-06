#!/bin/bash

###############################################################################
# Command Logger Script
# Logs every shell command with timestamp and working directory to a custom file.
# Coexists safely with other PROMPT_COMMAND loggers (e.g. .bashrc-based).
#
# Usage:
#   source command_logger.sh --start [logfile]   # Start logging (optional logfile)
#   source command_logger.sh --stop              # Stop logging (removes only this logger)
#
# Example:
#   source ./command_logger.sh --start ~/mylog.txt
#
# NOTE: Must be *sourced*, not executed, to affect current shell environment.
###############################################################################

# Default logfile
DEFAULT_LOGFILE=~/command_log.txt
LOGFILE="$2"

if [ -z "$LOGFILE" ]; then
    LOGFILE="$DEFAULT_LOGFILE"
fi

# Define our logger function
log_custom() {
  cmd=$(history 1)
  printf "%s  %s  %s\n" "$(date +"%d/%m/%y %T")" "$(pwd)" "${cmd#* }" >> "$LOGFILE"
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
    echo "Logs each shell command with timestamp and working directory."
    echo
    echo "Usage:"
    echo "  source $0 --start [logfile]    # Start logging (optional logfile)"
    echo "  source $0 --stop               # Stop this logger only"
    echo
    echo "NOTE: Run this script with 'source' or '.' so it affects your current shell."
    echo "Example:"
    echo "  source ./command_logger.sh --start ~/mylog.txt"
fi