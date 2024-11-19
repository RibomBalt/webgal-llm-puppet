#!/bin/bash
export HOST=$(ip r|grep default|awk '{print $9}')
export MOOD=1
cd backend && python app.py