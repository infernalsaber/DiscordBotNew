#!/bin/bash
kill -9 $(ps aux | grep -w "[b]ot_loop3.py" | awk '{print $2}')
echo "Stopped"