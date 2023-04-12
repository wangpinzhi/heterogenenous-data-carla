@echo off

@REM Variables
set ROOT_PATH=%1

echo "process cm_rgb7 cm_rgb6 cm_rgb1"

python tools/cubemap2pinhole.py   --fov 150^
                                        --cubeW 2560^
                                        --outH 1856^
                                        --outW 2880^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_new"^
                                        --camera "cm_rgb7"^
                                        --use_cuda
                                        

python tools/cubemap2pinhole.py   --fov 150^
                                        --cubeW 2560^
                                        --outH 1080^
                                        --outW 1920^
                                        --external_path "%ROOT_PATH%/external.txt"^
                                        --cubemap_dir "%ROOT_PATH%/cubemap"^
                                        --output_dir "%ROOT_PATH%/pinhole_new"^
                                        --camera "cm_rgb6"^
                                        --use_cuda
                                        

@REM python tools/cubemap2pinhole.py   --fov 150^
@REM                                         --cubeW 2560^
@REM                                         --outH 1856^
@REM                                         --outW 2880^
@REM                                         --external_path "%ROOT_PATH%/external.txt"^
@REM                                         --cubemap_dir "%ROOT_PATH%/cubemap"^
@REM                                         --output_dir "%ROOT_PATH%/pinhole_new"^
@REM                                         --camera "cm_rgb1"^
@REM                                         --use_cuda

python tools/cubemap2erp.py     --external_path "%ROOT_PATH%/external.txt"^
                                --cubeW 2560^
                                --format "npz"^
                                --cubemap_dir "%ROOT_PATH%/cubemap"^
                                --output_dir "%ROOT_PATH%/erp"^
                                --camera "cm_rgb0"^
                                --use_cuda
                                        
