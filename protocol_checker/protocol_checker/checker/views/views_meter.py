from django.http import HttpResponse
from ..models import CurrentTest, TestConfig, PastTest, Request, SuccessResponse, FailResponse
from django.core.exceptions import ObjectDoesNotExist
import time
import json
import core



# logging
import logging
logger = logging.getLogger('checker')


def get_meter_request(request, request_str, ts):
    post = request.META
    temp = post["HTTP_AUTHORIZATION"].split(':')
    access_key = temp[1]
    mac_sensor = temp[0].split()[1]
    try:
        row = CurrentTest.objects.get(mac=mac_sensor)
        row.save()
        return response_checking(CurrentTest.objects.get(mac=row.mac), request=request_str,
                                 access_key=access_key)
    except ObjectDoesNotExist:
        raise Exception("MAC address registration required")
    except:
        raise


def response_checking(current_query, request, access_key):
    error = False
    request_query = Request.objects.get(string=request)
    current_query.request = request_query
    record_row = PastTest(mac=current_query.mac, config_id=current_query.config_id,
                          status=current_query.status, request=request_query)
    record_row.save()

    try:
        response_query = TestConfig.objects.get(status=current_query.status, request_id=request_query.id,
                                                config_id=current_query.config_id)
        record_row.next_status = response_query.next_status
        record_row.save()

    except ObjectDoesNotExist as e:
        errormsg = {"exception": e, "status": current_query.status, "config_id": current_query.config}
        if current_query.status != 0:
            response_query = TestConfig.objects.get(status=current_query.status,
                                                    config_id=current_query.config_id)
            request_error = "request %s is expected" % response_query.request
            errormsg["error"] = request_error
        print errormsg
        return HttpResponse(errormsg)


    print "current status is %s" % current_query.status

    try:
        CurrentTest.objects.get(mac=current_query.mac, id=access_key)
        try:
            print response_query.response_id
            success_response_query = SuccessResponse.objects.get(response_ptr_id=response_query.response_id)
            success_response_query.json_content = json.loads(success_response_query.json_content)
            return json_response(error=error, json_data=success_response_query.json_content,
                                 current_query=current_query, response_query=response_query)
        except SuccessResponse.DoesNotExist:
            error = True
        except:
            raise
    except (CurrentTest.DoesNotExist, ValueError):
        try:
            success_response_query = SuccessResponse.objects.get(response_ptr_id=response_query.response_id)
            if success_response_query.json_content == '{"access_key": "AK"}':
                response_data = {"access_key": str(current_query.id)}
                return json_response(error=error, json_data=response_data,
                                     current_query=current_query, response_query=response_query)
        except SuccessResponse.DoesNotExist:
            error = True
        except:
            raise
    finally:
        if error:
            fail_response_body = {}
            fail_response_query = FailResponse.objects.get(response_ptr_id=response_query.response_id)
            fail_response_body['code'] = fail_response_query.code
            fail_response_body['message'] = fail_response_query.message
            return json_response(status=fail_response_query.http_status, error=error,
                                 json_data=fail_response_body,
                                 current_query=current_query, response_query=response_query)


def json_response(error, status=None, current_query=None, response_query=None,
                  request=None, json_data=None):
    current_query.status = response_query.next_status
    if current_query.status == -1:
        current_query.delete()
    else:
        current_query.save()
    print "current status %s" % current_query.status
    data = json.dumps(json_data)
    if error:
        return HttpResponse(content=data, status=status)
    else:
        return HttpResponse(content=data)








