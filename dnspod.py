from __future__ import annotations

import json
import os
import tomllib
from dataclasses import dataclass

from tencentcloud.common import credential  # type:ignore
from tencentcloud.common.profile.client_profile import ClientProfile  # type:ignore
from tencentcloud.common.profile.http_profile import HttpProfile  # type:ignore
from tencentcloud.dnspod.v20210323 import dnspod_client, models  # type:ignore

from utils import CommonModel


@dataclass
class CredProvider:
    sid: str
    skey: str

    @staticmethod
    def from_file(path: str) -> CredProvider:
        path = os.path.expanduser(path)
        
        with open(path, "rb") as f:
            data = tomllib.load(f)
        _ = data["dns_edit"]
        return CredProvider(
            _["tencent_cloud_secret_id"],
            _["tencent_cloud_secret_key"],
        )


def change_dns(
    ip_address: str, domain: str = "s-2.link", sub_domain: str = "init"
) -> dict:
    rtn = CommonModel(stage="change_dns")
    resp = None
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey,此处还需注意密钥对的保密
        # 密钥可前往https://console.cloud.tencent.com/cam/capi网站进行获取
        c = CredProvider.from_file(
            "~/.tencent_cloud/credentials"
        )
        cred = credential.Credential(c.sid, c.skey)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = dnspod_client.DnspodClient(cred, "", clientProfile)

        # 1. Get RecordID

        req = models.DescribeRecordListRequest()
        req.from_json_string(json.dumps({
            "Domain": domain,
            "Subdomain": sub_domain,
        }))

        # 返回的resp是一个DescribeDomainListResponse的实例，与请求对象对应
        resp = client.DescribeRecordList(req)

        # Get record ID
        record_id = json.loads(resp.to_json_string())["RecordList"][0]["RecordId"]

        # 2. Change DNS record

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.ModifyRecordRequest()
        params = {
            "Domain": domain,
            "SubDomain": sub_domain,
            "RecordType": "A",
            "Value": ip_address,
            "RecordId": record_id,
            "RecordLine": "默认",
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个ModifyRecordResponse的实例，与请求对象对应
        resp = client.ModifyRecord(req)

    except Exception as e:
        rtn.when_except(e)

    finally:
        if resp is not None:
            rtn.detail = json.loads(resp.to_json_string())
        else:
            rtn.detail = {}
        return rtn
