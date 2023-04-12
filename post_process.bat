@echo off
set root_path=huawei_cmp_ori
python post_process.py  --num_workers 2^
                        --gpu 0^
                        --batch_size 4^
                        --sensor_config_json "output/%root_path%/configs/sensor_config.json"^
                        --raw_data_dir "output/%root_path%/raw_data"^
                        --save_dir "output/%root_path%/post_data_new"^