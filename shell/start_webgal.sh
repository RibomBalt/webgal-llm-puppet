#!/bin/bash
cd WebGAL && yarn build && cd packages/webgal/dist && python -m http.server 3000