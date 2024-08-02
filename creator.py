from tkinter import Button, BooleanVar, Checkbutton, Label, StringVar, Frame, OptionMenu, Entry
from tkinter import TRUE, FALSE, N, W, LEFT
from utils import resource_path
from bot_related.bot_config import BotConfig
from filepath.file_relative_paths import FilePaths
import os
import traceback
import json


def button(frame, on_click=lambda v: v, **kwargs):
    btn = Button(frame, **kwargs)
    def command():
        on_click(btn)
    btn.config(command=command)
    return btn


def checkbox_fn_creator(name, text):
    def title_checkbox(app, parent, on_click=lambda v: v):
        variable = BooleanVar()
        variable.set(TRUE if getattr(app.bot_config, name) else FALSE)
        def command():
            setattr(app.bot_config, name, variable.get())
            write_bot_config(app.bot_config, app.device.serial.replace(':', "_"))
            on_click(variable.get())
        checkbox = Checkbutton(parent, text=text, variable=variable, command=command)
        return checkbox, variable
    return title_checkbox


def entry_int_fn_creator(name, begin_text, end_text=None):
    def entry(app, parent):
        str_value = StringVar()
        str_value.set(str(getattr(app.bot_config, name)))
        frame = Frame(parent)
        label = Label(frame, text=begin_text)
        entry = Entry(frame, textvariable=str_value)
        def creator(attr_name):
            def validate_cmd(value, action_type):
                if action_type == '1':
                    if not value.isdigit():
                        return False
                    if value[0] == '0':
                        return False
                setattr(app.bot_config, attr_name, int(value if value != '' else '1'))
                write_bot_config(app.bot_config, app.device.serial.replace(':', "_"))
                return True
            return validate_cmd
        entry.config(width=10, validate='key', validatecommand=(
            frame.register(creator(name)), '%P', '%d'
        ))
        label.grid(row=0, column=0, sticky=N + W, padx=5)
        entry.grid(row=0, column=1, sticky=N + W, padx=5)
        if end_text is not None:
            Label(frame, text=end_text).grid(row=0, column=2, sticky=N+W, padx=5)
        return frame, None
    return entry


def train_fn_creator(name, train_attr_name, upgrade_attr_name):
    lv_training_options = ['1', '2', '3', '4', '5', 'Disabled']
    lv_upgrade_options = ['1', '2', '3', '4', '5', 'All', 'Disabled']
    def num_to_option_value(num):
        return str(num + 1 if 0 <= num <= 4 else 'All' if num == 5 else 'Disable')
    def option_value_to_num(v):
        return int(v if v != 'All' and v != 'Disabled' else 6 if v == 'All' else 0) - 1
    def train(app, parent):
        frame = Frame(parent)
        name_tag = Label(frame, text=name)
        def update_command(v):
            setattr(app.bot_config, upgrade_attr_name, option_value_to_num(v))
            write_bot_config(app.bot_config, app.device.serial.replace(':', "_"))
        upgrade_label = Label(frame, text='Upgrade Lv.')
        upgrade_variable = StringVar()
        upgrade_variable.set(num_to_option_value(getattr(app.bot_config, upgrade_attr_name)))
        upgrade_option = OptionMenu(frame, upgrade_variable, *lv_upgrade_options, command=update_command)
        def train_command(v):
            setattr(app.bot_config, train_attr_name, option_value_to_num(v))
            write_bot_config(app.bot_config, app.device.serial.replace(':', "_"))
        train_label = Label(frame, text='Training Lv.')
        train_variable = StringVar()
        train_variable.set(num_to_option_value(getattr(app.bot_config, train_attr_name)))
        train_option = OptionMenu(frame, train_variable, *lv_training_options, command=train_command)
        name_tag.config(width=8, anchor=N + W, justify=LEFT)
        upgrade_option.config(width=8)
        train_option.config(width=8)
        frame.columnconfigure(0, weight=5)
        name_tag.grid(row=0, column=0)
        train_label.grid(row=0, column=2)
        train_option.grid(row=0, column=3)
        upgrade_label.grid(row=0, column=4)
        upgrade_option.grid(row=0, column=5)
        return frame, None
    return train


def load_bot_config(prefix):
    try:
        config_path = resource_path(FilePaths.SAVE_FOLDER_PATH.value + '{}_config.json'.format(prefix))
        if not os.path.exists(config_path):
            print(f"Config file not found: {config_path}. Using default configuration.")
            return BotConfig()  # Trả về cấu hình mặc định hoặc bạn có thể tạo file mới
        with open(config_path) as f:
            config_dict = json.load(f)
            config = BotConfig(config_dict)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {config_path}: {e}")
        config = BotConfig()
    except Exception as e:
        traceback.print_exc()
        config = BotConfig()
    return config


def write_bot_config(bot_config, prefix):
    save_dir = resource_path(FilePaths.SAVE_FOLDER_PATH.value)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, "{}_config.json".format(prefix))
    with open(file_path, 'w') as f:
        f.write(json.dumps(bot_config.to_dict()))


def load_building_pos(prefix):
    try:
        pos_path = resource_path(FilePaths.SAVE_FOLDER_PATH.value + "{}_building_pos.json".format(prefix))
        if not os.path.exists(pos_path):
            print(f"Building position file not found: {pos_path}. Returning None.")
            return None
        with open(pos_path) as f:
            content = f.read().strip()
            if not content:
                print(f"Building position file is empty: {pos_path}. Returning None.")
                return None
            building_pos = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {pos_path}: {e}")
        return None
    except Exception as e:
        traceback.print_exc()
        return None
    return building_pos


def write_building_pos(building_pos, prefix):
    building_pos_json = json.dumps(building_pos)
    with open(resource_path(FilePaths.SAVE_FOLDER_PATH.value + "{}_building_pos.json".format(prefix)), 'w') as f:
        f.write(building_pos_json)


def load_device_config():
    try:
        with open(resource_path('devices_config.json')) as f:
            config = json.load(f)
    except Exception as e:
        config = []
    return config


def write_device_config(config):
    config_json = json.dumps(config)
    with open(resource_path("devices_config.json"), 'w') as f:
        f.write(config_json)


def init_building_position(app):
    prefix = app.device.serial.replace(':', "_")
    building_pos = load_building_pos(prefix)
    if building_pos is None:
        # Chạy mã để thiết lập vị trí tòa nhà
        building_pos = {
            "barracks": (100, 200),
            # Thêm các tòa nhà khác tại đây
        }
        write_building_pos(building_pos, prefix)
    else:
        print("Building positions already set. Skipping initialization.")
