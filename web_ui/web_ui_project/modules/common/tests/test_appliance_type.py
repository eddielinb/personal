import unittest

from appliance_type import ApplianceType


class TestApplianceType(unittest.TestCase):
    def setUp(self):
        self._appliance_type = {
            1: ["Air Cleaner", 1],
            2: ["Air Conditioner", 1],
            3: ["Ceiling Fan", 1],
            4: ["Clothes Iron", 1],
            5: ["Clothes Washer", 1],
            6: ["Coffee Maker", 1],
            7: ["Desk Lamp", 1],
            8: ["Electric Heater", 1],
            9: ["Electric Kettle", 1],
            10: ["Electric Piano", 1],
            11: ["Electric Pot", 1],
            12: ["Floor Heating", 1],
            13: ["Food Mixer", 1],
            14: ["Gaming Player", 1],
            15: ["Hair Dryer", 1],
            16: ["Humidifier", 1],
            17: ["Image Scanner", 1],
            18: ["Kotatsu", 1],
            19: ["Laptop PC", 1],
            20: ["Microwave", 1],
            21: ["Music Player", 1],
            22: ["Overhead Lighting", 1],
            23: ["Printer", 1],
            24: ["Refrigerator", 1],
            25: ["Rice Cooker", 1],
            26: ["Tablet", 1],
            27: ["Telephone", 1],
            28: ["Toaster", 1],
            29: ["Toilet", 1],
            30: ["TV", 1],
            31: ["Vacuum Cleaner", 1],
            32: ["Vent Fan", 1],
            33: ["Video Recorder", 1],
            34: ["Dish Washer", 1],
            35: ["Oven", 1],
            36: ["Bread Machine", 1],
            37: ["IH", 1],
            38: ["Bath Dryer", 1],
            39: ["EcoCute", 1],
            40: ["Thermal Storage Heater", 1],
            41: ["Electric Water Heater", 1],
            300: ["Kettle/Hair Dryer", 2],
            301: ["Heater", 2],
            302: ["Hari", 2],
            303: ["Extreme Heat", 2],
            304: ["Light", 2],
            308: ["Home Appliance", 2],
            309: ["Power Generator", 2],
            310: ["Outlet Load", 2],
            800: ["Motion Sensor", 99],
            994: ["Other Generator", 3],
            995: ["Main Breaker", 99],
            996: ["FC", 3],
            997: ["PV", 3],
            998: ["Background", 99],
            999: ["Unknown", 99]
        }

    def tearDown(self):
        pass

    def test_get_all_appliance_types(self):
        atypes = ApplianceType.get_all_appliance_types()

        self.assertEqual(len(atypes), len(self._appliance_type))
        for key in self._appliance_type.keys():
            self.assertEqual(self._appliance_type[key][0], atypes[key]["name"])
            self.assertEqual(self._appliance_type[key][1], atypes[key]["type"])
