from ..models import (Config, TestConfig, CurrentTest, CheckingProcedure, CompletedTest, PastTest)
from django.core.exceptions import ObjectDoesNotExist
# import time


class ClientList:
    def __init__(self, model_object, headings):
        self.model_object = model_object

        if not isinstance(headings, (dict, list)):
            raise TypeError(
                "{} needs headings of type list or dict".format(self.__name__))
        self.headings = headings

    def get(self):
        config_ids = self.ids()
        return_dict = {
            'headings': self.get_headings(),
            'rows': [
                {
                    'values': row,
                    'id': config_ids.next()
                } for row in self.rows()]}
        # print return_dict
        return return_dict

    def get_headings(self):
        if isinstance(self.headings, dict):
            return self.headings.values()
        elif isinstance(self.headings, list):
            return self.headings

    def get_rows(self):
        rows = self.model_object.objects.all()
        return [
            [getattr(row, heading) for heading in self.headings]
            for row in rows
            ]

    def rows(self):
        rows = self.model_object.objects.filter(status=0)
        for row in rows:
            yield [getattr(row, heading) for heading in self.headings]

    def get_ids(self):
        rows = self.model_object.objects.all()
        return [row.id for row in rows]

    def ids(self):
        rows = self.model_object.objects.all()
        for row in rows:
            yield row.id

pendingList = ClientList(CurrentTest, {
    'mac': "Mac Address",
    'config': "Config",
    'created': "Created (UTC)",
})

configList = ClientList(Config, {
    'name': "Name"
})


class InProgressList(object):
    def __init__(self):
        pass

    def get(self):
        return {
            'headings': self._get_headings(),
            'rows': self.get_rows_and_mac()
        }

    def get_rows_and_mac(self):
        pending_list = []
        try:
            for row in self._get_rows():
                pending_list.append({"row": row, "mac": row[0]})
            return pending_list
        except ObjectDoesNotExist:
            return pending_list
        # TODO: Remove
        except:
            raise


    @staticmethod
    def _get_headings():
        return [
            "mac", "status", "config_id", "timestamp", "request",
        ]

    def _get_rows(self):
        pending_list = []
        try:
            rows = CurrentTest.objects.exclude(status=-1)
            for count in range(rows.count()):
                pending_list.append([
                    rows[count].mac,
                    rows[count].status,
                    rows[count].config,
                    rows[count].updated,
                    rows[count].request,
                ])
            return pending_list
        except ObjectDoesNotExist:
            return pending_list
        # TODO: Remove
        except:
            raise


# class InProgressDetail(InProgressList):
#     def __init__(self):
#         super(InProgressDetail, self).__init__()
#
#     def _get_rows(self):
#         pending_list = []
#         try:
#             rows = PastTest.objects.exclude(status=-1 or 0)
#             for count in range(rows.count()):
#                 pending_list.append([
#                     rows[count].mac,
#                     rows[count].status,
#                     rows[count].config,
#                     rows[count].timestamp,
#                     rows[count].request,
#                 ])
#             return pending_list
#         except ObjectDoesNotExist:
#             return pending_list
#         # TODO: Remove
#         except:
#             raise


class TestDetailList(InProgressList):
    def __init__(self, mac, config):
        super(TestDetailList, self).__init__()
        self._mac = mac
        self._config = config

    def get(self):
        return {
            'headings': self._get_headings(),
            'rows': self._get_rows()
        }

    def _get_rows(self):
        pending_list = []
        try:
            rows = PastTest.objects.filter(mac=self._mac,
                                           config_id=self._config)
            for count in range(rows.count()):
                pending_list.append([
                    rows[count].mac,
                    rows[count].status,
                    rows[count].config,
                    rows[count].timestamp,
                    rows[count].request,
                ])
            return pending_list
        except ObjectDoesNotExist:
            return pending_list
        # TODO: Remove
        except:
            raise


class CompletedList(object):
    def __int__(self):
        pass

    def get(self):
        return {
            'headings': self._get_headings(),
            'rows': self._get_completed_list()
        }

    @staticmethod
    def _get_headings():
        return [
            "mac", "config_id", "timestamp"
        ]

    @staticmethod
    def _get_completed_list():
        completed_list = []
        try:
            rows = PastTest.objects.filter(next_status=-1)
            for count in range(rows.count()):
                completed_list.append([
                    rows[count].mac,
                    rows[count].config,
                    rows[count].timestamp
                ])
            return completed_list
        except ObjectDoesNotExist:
            return completed_list
        # TODO: Remove
        except:
            raise


def add_pending(config_id, mac_sensor):
    try:
        existed_row = CurrentTest.objects.get(mac=mac_sensor, config_id=config_id)
        return True
    except CurrentTest.DoesNotExist:
        try:
            existed_row = PastTest.objects.filter(mac=mac_sensor, config_id=config_id)
            return True
        except PastTest.DoesNotExist:
            new_row = CurrentTest(mac=mac_sensor,
                                  config_id=config_id,
                                  status=0)
            new_row.save()
            return False
        except:
            raise
    except:
        raise



def remove_pending(current_id):
    try:
        row = CurrentTest.objects.get(id=current_id)
        row.delete()
    except CurrentTest.DoesNotExist:
        raise


def remove_history(mac):
    rows = PastTest.objects.filter(mac=mac)
    rows.delete()
    try:
        rows = CurrentTest.objects.get(mac=mac)
        rows.delete()
    except CurrentTest.DoesNotExist:
        pass