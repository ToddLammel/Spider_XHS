import aiohttp
import asyncio
import json

from loguru import logger

from apis.pc_apis import XhsApi


if __name__ == '__main__':
    cookies = r'abRequestId=92fcc04b-656b-509f-8a1e-c3ac8e497f23; a1=1956beb135e5lv46l69faxnx5tbuna61jz5pwoev850000427689; webId=e78b2e096f0b8a5aab4ee52ffa364b7d; gid=yj2KDdDJdfVDyj2KDdDyquld2d21h4K1Kji02hYCIC29DU287I0KyE8884JWKYj8S8ySSW80; x-user-id-creator.xiaohongshu.com=5e24fb75000000000100509f; customerClientId=942161409810786; access-token-creator.xiaohongshu.com=customer.creator.AT-68c517486023646732033249ppejtee9xgofm0jp; galaxy_creator_session_id=gMM7NUHERAH9g2VJs89BsXjoRkhcUTGcu5FV; galaxy.creator.beaker.session.id=1742975704346011423609; xsecappid=xhs-pc-web; web_session=0400698f50b83d5600c98361d9354b8bb5902b; webBuild=4.62.1; acw_tc=0a4a661517438347833435632e23dabb3dc4399a0de12944f921ceec5e715e; unread={%22ub%22:%2267e5cd6a000000001a007a3b%22%2C%22ue%22:%2267e23cbe000000000603e2cc%22%2C%22uc%22:18}; loadts=1743835074786; websectiga=9730ffafd96f2d09dc024760e253af6ab1feb0002827740b95a255ddf6847fc8; sec_poison_id=a51d1970-f16e-4338-9763-15f76e46de95'
    xhs_apis = XhsApi(cookies=cookies)


    async def test():
        success, msg, res_json = await xhs_apis.search_some_note('人口', require_num=10)
        logger.info(f'登录结果 {json.dumps(res_json, ensure_ascii=False)}: {success}, msg: {msg}')


    asyncio.run(test())
