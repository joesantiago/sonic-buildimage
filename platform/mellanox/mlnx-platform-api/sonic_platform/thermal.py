#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the thermals data which are available in the platform
#
#############################################################################

try:
    from sonic_platform_base.thermal_base import ThermalBase
    from sonic_daemon_base.daemon_base import Logger
    from os import listdir
    from os.path import isfile, join
    import io
    import os.path
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

# Global logger class instance
logger = Logger()

THERMAL_DEV_CATEGORY_CPU_CORE = "cpu_core"
THERMAL_DEV_CATEGORY_CPU_PACK = "cpu_pack"
THERMAL_DEV_CATEGORY_MODULE = "module"
THERMAL_DEV_CATEGORY_PSU = "psu"
THERMAL_DEV_CATEGORY_GEARBOX = "gearbox"
THERMAL_DEV_CATEGORY_AMBIENT = "ambient"

THERMAL_DEV_ASIC_AMBIENT = "asic_amb"
THERMAL_DEV_FAN_AMBIENT = "fan_amb"
THERMAL_DEV_PORT_AMBIENT = "port_amb"
THERMAL_DEV_COMEX_AMBIENT = "comex_amb"
THERMAL_DEV_BOARD_AMBIENT = "board_amb"

THERMAL_API_GET_TEMPERATURE = "get_temperature"
THERMAL_API_GET_HIGH_THRESHOLD = "get_high_threshold"

HW_MGMT_THERMAL_ROOT = "/var/run/hw-management/thermal/"

thermal_api_handler_cpu_core = {
    THERMAL_API_GET_TEMPERATURE:"cpu_core{}",
    THERMAL_API_GET_HIGH_THRESHOLD:"cpu_core{}_max"
}
thermal_api_handler_cpu_pack = {
    THERMAL_API_GET_TEMPERATURE:"cpu_pack",
    THERMAL_API_GET_HIGH_THRESHOLD:"cpu_pack_max"
}
thermal_api_handler_module = {
    THERMAL_API_GET_TEMPERATURE:"module{}_temp_input",
    THERMAL_API_GET_HIGH_THRESHOLD:"module{}_temp_crit"
}
thermal_api_handler_psu = {
    THERMAL_API_GET_TEMPERATURE:"psu{}_temp",
    THERMAL_API_GET_HIGH_THRESHOLD:"psu{}_temp_max"
}
thermal_api_handler_gearbox = {
    THERMAL_API_GET_TEMPERATURE:"gearbox{}_temp_input",
    THERMAL_API_GET_HIGH_THRESHOLD:None
}
thermal_ambient_apis = {
    THERMAL_DEV_ASIC_AMBIENT : "asic",
    THERMAL_DEV_PORT_AMBIENT : "port_amb",
    THERMAL_DEV_FAN_AMBIENT : "fan_amb",
    THERMAL_DEV_COMEX_AMBIENT : "comex_amb",
    THERMAL_DEV_BOARD_AMBIENT : "board_amb"
}
thermal_ambient_name = {
    THERMAL_DEV_ASIC_AMBIENT : "Ambient ASIC Temp",
    THERMAL_DEV_PORT_AMBIENT : "Ambient Port Side Temp",
    THERMAL_DEV_FAN_AMBIENT : "Ambient Fan Side Temp",
    THERMAL_DEV_COMEX_AMBIENT : "Ambient COMEX Temp",
    THERMAL_DEV_BOARD_AMBIENT : "Ambient Board Temp"
}
thermal_api_handlers = {
    THERMAL_DEV_CATEGORY_CPU_CORE : thermal_api_handler_cpu_core, 
    THERMAL_DEV_CATEGORY_CPU_PACK : thermal_api_handler_cpu_pack,
    THERMAL_DEV_CATEGORY_MODULE : thermal_api_handler_module,
    THERMAL_DEV_CATEGORY_PSU : thermal_api_handler_psu,
    THERMAL_DEV_CATEGORY_GEARBOX : thermal_api_handler_gearbox
}
thermal_name = {
    THERMAL_DEV_CATEGORY_CPU_CORE : "CPU Core {} Temp", 
    THERMAL_DEV_CATEGORY_CPU_PACK : "CPU Pack Temp",
    THERMAL_DEV_CATEGORY_MODULE : "xSFP module {} Temp",
    THERMAL_DEV_CATEGORY_PSU : "PSU-{} Temp",
    THERMAL_DEV_CATEGORY_GEARBOX : "Gearbox {} Temp"
}

thermal_device_categories_all = [
    THERMAL_DEV_CATEGORY_CPU_CORE,
    THERMAL_DEV_CATEGORY_CPU_PACK,
    THERMAL_DEV_CATEGORY_MODULE,
    THERMAL_DEV_CATEGORY_PSU,
    THERMAL_DEV_CATEGORY_AMBIENT,
    THERMAL_DEV_CATEGORY_GEARBOX
]

thermal_device_categories_singleton = [
    THERMAL_DEV_CATEGORY_CPU_PACK,
    THERMAL_DEV_CATEGORY_AMBIENT
]
thermal_api_names = [
    THERMAL_API_GET_TEMPERATURE,
    THERMAL_API_GET_HIGH_THRESHOLD
]

hwsku_dict_thermal = {'ACS-MSN2700': 0, 'LS-SN2700':0, 'ACS-MSN2740': 3, 'ACS-MSN2100': 1, 'ACS-MSN2410': 2, 'ACS-MSN2010': 4, 'ACS-MSN3700': 5, 'ACS-MSN3700C': 6, 'Mellanox-SN2700': 0, 'Mellanox-SN2700-D48C8': 0, 'ACS-MSN3800': 7}
thermal_profile_list = [
    # 2700
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 2),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 2100
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 16),
        THERMAL_DEV_CATEGORY_PSU:(0, 0),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,0),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 2410
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 2),
        THERMAL_DEV_CATEGORY_MODULE:(1, 56),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 2740
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,0),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 2010
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 22),
        THERMAL_DEV_CATEGORY_PSU:(0, 0),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,0),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 3700
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 3700c
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 2),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 3800
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 64),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(1,32),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
]

def initialize_thermals(sku, thermal_list, psu_list):
    # create thermal objects for all categories of sensors
    tp_index = hwsku_dict_thermal[sku]
    thermal_profile = thermal_profile_list[tp_index]
    for category in thermal_device_categories_all:
        if category == THERMAL_DEV_CATEGORY_AMBIENT:
            count, ambient_list = thermal_profile[category]
            for ambient in ambient_list:
                thermal = Thermal(category, ambient, True)
                thermal_list.append(thermal)
        else:
            start, count = 0, 0
            if category in thermal_profile:
                start, count = thermal_profile[category]
                if count == 0:
                    continue
            if count == 1:
                thermal = Thermal(category, 0, False)
                thermal_list.append(thermal)
            else:
                if category == THERMAL_DEV_CATEGORY_PSU:
                    for index in range(count):
                        thermal = Thermal(category, start + index, True, psu_list[index].get_powergood_status, "power off")
                        thermal_list.append(thermal)
                else:
                    for index in range(count):
                        thermal = Thermal(category, start + index, True)
                        thermal_list.append(thermal)

class Thermal(ThermalBase):
    def __init__(self, category, index, has_index, dependency = None, hint = None):
        """
        index should be a string for category ambient and int for other categories
        """
        if category == THERMAL_DEV_CATEGORY_AMBIENT:
            self.name = thermal_ambient_name[index]
            self.index = index
        elif has_index:
            self.name = thermal_name[category].format(index)
            self.index = index
        else:
            self.name = thermal_name[category]
            self.index = 0

        self.category = category
        self.temperature = self._get_file_from_api(THERMAL_API_GET_TEMPERATURE)
        self.high_threshold = self._get_file_from_api(THERMAL_API_GET_HIGH_THRESHOLD)
        self.dependency = dependency
        self.dependent_hint = hint

    def get_name(self):
        """
        Retrieves the name of the device

        Returns:
            string: The name of the device
        """
        return self.name

    def _read_generic_file(self, filename, len):
        """
        Read a generic file, returns the contents of the file
        """
        result = None
        try:
            with open(filename, 'r') as fileobj:
                result = fileobj.read()
        except Exception as e:
            logger.log_info("Fail to read file {} due to {}".format(filename, repr(e)))
        return result

    def _get_file_from_api(self, api_name):
        if self.category == THERMAL_DEV_CATEGORY_AMBIENT:
            if api_name == THERMAL_API_GET_TEMPERATURE:
                filename = thermal_ambient_apis[self.index]
            else:
                return None
        else:
            handler = thermal_api_handlers[self.category][api_name]
            if self.category in thermal_device_categories_singleton:
                filename = handler
            else:
                filename = handler.format(self.index)
        return join(HW_MGMT_THERMAL_ROOT, filename)

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal

        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125 
        """
        if self.dependency and not self.dependency():
            if self.dependent_hint:
                hint = self.dependent_hint
            else:
                hint = "unknown reason"
            logger.log_info("get_temperature for {} failed due to {}".format(self.name, hint))
            return None
        value_str = self._read_generic_file(self.temperature, 0)
        if value_str is None:
            return None
        value_float = float(value_str)
        return value_float / 1000.0

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.high_threshold is None:
            return None
        value_str = self._read_generic_file(self.high_threshold, 0)
        if value_str is None:
            return None
        value_float = float(value_str)
        return value_float / 1000.0
