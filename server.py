import boto3  # type:ignore
from fastapi import FastAPI  # type:ignore

from utils import CommonModel
from lightsail import renew, clean_up
from dnspod import change_dns


app = FastAPI()


@app.get('/renew/{instance_name}', response_model=CommonModel)
async def renew_static_ipv4(instance_name: str, debug: bool = False) -> CommonModel:
    rtn = CommonModel(stage='Server')
    client = boto3.client('lightsail')
    renew_response = None
    dns_response = None

    try:
        renew_response = renew(client, instance_name, debug)
        dns_response = change_dns(
            ip_address=renew_response.detail['new_ip'],
            domain='s-2.link',
            sub_domain='init',
        )

    except Exception as e:
        rtn.when_except(e)

    finally:
        clean_response = clean_up(client)
        rtn.detail = {
            'renew': renew_response,
            'dns': dns_response,
            'clean_up': clean_response,
        }
        return rtn
