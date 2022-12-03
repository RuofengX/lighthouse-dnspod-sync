import uuid
from typing import Dict

from utils import CommonModel


def random_str(length: int = 6) -> str:
    return uuid.uuid4().hex[:length]


def clean_up(client, debug: bool = False) -> CommonModel:
    rtn = CommonModel(stage='clean_up')
    try:
        static_ipv4_list = client.get_static_ips()["staticIps"]
        old_ipv4_list = static_ipv4_list

        release_list = []
        for ip in static_ipv4_list:
            if not ip["isAttached"]:
                name = ip["name"]
                release_list.append(
                    client.release_static_ip(staticIpName=name)
                )

    except Exception as e:
        rtn.when_except(e)

    finally:
        if debug:
            rtn.detail = {
                'old_ipv4_list': old_ipv4_list,
                'release_list': release_list,
            }
        return rtn


def renew(
    client, instance_name: str, debug: bool = False
) -> CommonModel:

    rtn = CommonModel(stage='renew')
    detail: Dict[str, str | dict] = {
        'new_ip': '',
        'old_ip': '',
    }
    extra = {
        'step': '0',
    }

    try:
        # 1. Prepare
        # 1.1 get instance's old ipv4 address
        extra['step'] = '1.1'
        old_status_response = client.get_instance(instanceName=instance_name)
        old_ip_address = old_status_response["instance"]["publicIpAddress"]
        detail['old_ip'] = old_ip_address
        extra["11_old_status_response"] = old_status_response

        # 1.2 get ipv4 lists
        extra['step'] = '1.2'
        static_ipv4_list = client.get_static_ips()['staticIps']
        extra["12_old_ipv4_list"] = static_ipv4_list

        # 1.3 allocate new ip
        extra['step'] = '1.3'
        new_ip_name = f"auto-{random_str()}"
        allocate_ip_response = client.allocate_static_ip(staticIpName=new_ip_name)
        assert (
            allocate_ip_response["operations"][0]["resourceName"] == new_ip_name
        ), "IP resource create fail or resource name is error."

        # 2. Detach old IP
        # 2.1 find name
        extra['step'] = '2.1'
        for ip in static_ipv4_list:
            if old_ip_address == ip["ipAddress"]:
                old_ipv4_name = ip["name"]
                break

        # 2.2 detach
        extra['step'] = '2.2'
        detach_ip_response = client.detach_static_ip(
            staticIpName=old_ipv4_name,
        )
        extra["2_detach_ip_response"] = detach_ip_response

        # 3. Attach new IP
        extra['step'] = '3'
        attach_ip_response = client.attach_static_ip(
            staticIpName=new_ip_name,
            instanceName=instance_name,
        )
        extra["3_attach_ip_response"] = attach_ip_response

        # 4. Get new ip address
        extra['step'] = '4'
        new_status_response = client.get_instance(instanceName=instance_name)
        extra["4_new_status_response"] = new_status_response

        detail['new_ip'] = new_status_response["instance"]["publicIpAddress"]

    except Exception as e:
        rtn.when_except(e)

    finally:
        if debug:
            detail['extra'] = extra
        rtn.detail = detail
        return rtn
