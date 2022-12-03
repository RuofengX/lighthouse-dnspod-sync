# XRAY-Refresh

Allocate and re-attach Lighthouse IPv4 address, and sync to DNSPod.
Using boto3, FastAPI and TencentCloud's python SDK.

## About Cred

AWS credential is allocated in `~/.aws/credentials`

Tencent cloud secret id and key are imported by class `dnspod.CredProvider`

## Start server

Install all the dependence, using `pip install -r requirements.txt`.
A vitrual environment is recommended.
Development environment is `Python 3.11`.

Then Use `uvicorn server:app --reload` to start the api service.

