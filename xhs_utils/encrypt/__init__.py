import json
import time

from encrypt.params import *
from encrypt.misc_encrypt import MiscEncrypt
from encrypt.xs_encrypt import XsEncrypt
from encrypt.xsc_encrypt import XscEncrypt



def cookies_to_dict(cookies: str) -> dict:
    if '; ' in cookies:
        ck = {i.split('=')[0]: '='.join(i.split('=')[1:]) for i in cookies.split('; ')}
    else:
        ck = {i.split('=')[0]: '='.join(i.split('=')[1:]) for i in cookies.split(';')}
    return ck


async def generate_params(url: str, data: dict=None, cookies: str=None):
    x_t = int(time.time() * 1_000)

    _misc_encrypt = MiscEncrypt()
    x_b3_traceid = await _misc_encrypt.x_b3_traceid()
    x_ray_traceid = await _misc_encrypt.x_xray_traceid(x_b3_traceid)

    _xs_encrypt = XsEncrypt()
    ck = cookies_to_dict(cookies)
    x_s = await _xs_encrypt.encrypt_xs(url=url, a1=ck['a1'], ts=str(x_t), platform='xhs-pc-web')

    _xsc_encrypt = XscEncrypt()
    x_s_c = await _xsc_encrypt.encrypt_xsc(xs=x_s,
                                           xt=str(x_t),
                                           platform='xhs-pc-web',
                                           a1=ck['a1'],
                                           x1='3.8.7',
                                           x4='4.45.1',
                                           b1=browser_fingerprint)
    x_s_c = await XscEncrypt.b64_encode(x_s_c)

    headers['x-s'] = x_s
    headers['x-t'] = str(x_t)
    headers['x-s-common'] = x_s_c
    headers['x-b3-traceid'] = x_b3_traceid
    headers['x-xray-traceid'] = x_ray_traceid
    if data:
        data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    return headers, ck, data
