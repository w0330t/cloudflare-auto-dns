from adguardhome import AdGuardHome
from typing import Union

import pandas as pd
import asyncio
import subprocess
import toml
import os
import logging


def init_logger() -> logging.Logger:
    """初始化日志记录器

    Returns: 
        logging.Logger: 返回一个配置好的日志记录器 
    """ 
    # 配置日志级别
    logging.basicConfig(level=logging.DEBUG)
    # 创建日志记录器
    logger = logging.getLogger('logger')
    # 创建一个处理器，用于将日志保存到文件中
    file_handler = logging.FileHandler('log.txt')
    file_handler.setLevel(logging.DEBUG)
    # 创建一个格式化器，设置日志的格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # 把格式化器添加到处理器
    file_handler.setFormatter(formatter)
    # 把处理器添加到日志记录器
    logger.addHandler(file_handler)
    return logger

    

def check_domain(domain:str, adguard_domain_list:dict) -> Union[dict, None]:
    """检查域名是否存在

    Args:
        domain (str): 域名
        adguard_domain_list (dict): adguard的域名列表

    Returns:
        Union[dict, None]: 返回域名对象
    """ 
    for dic in adguard_domain_list:
        if dic['domain'] == domain:
            return dic
    return None


async def main():
    """主程序
    """
    # 导入config.toml
    config = toml.load('config.toml')

    logger = init_logger()

    os.chdir('CloudflareST/')
    subprocess.run(['./CloudflareST', '-url', config['test_url']])

    # 读取结果
    best_ip = pd.read_csv('result.csv').loc[0, 'IP 地址']

    async with AdGuardHome(host=config['ad_guard_home_url'], 
                        port=config['ad_guard_home_port'], 
                        username=config['ad_guard_home_username'], 
                        password=config['ad_guard_home_passwd']) as adguard:
        list = await adguard.request(uri='rewrite/list')

        for domain in config['domains']:
            result = check_domain(domain=domain, adguard_domain_list=list)
            put_data = {
                        "answer": best_ip,
                        "domain": domain
            }
            if result is not None:
                update_data = {
                    "target": result,
                    "update": put_data,
                }
                await adguard.request(uri='rewrite/update', method='PUT', json_data=update_data)
                logger.info(f'{domain} has been updated, ip is {best_ip}')
            else:
                await adguard.request(uri='rewrite/add', method='POST', json_data=put_data)
                logger.info(f'{domain} has been added, ip is {best_ip}')

        list = await adguard.request(uri='rewrite/list')
        logger.debug(list)

        logger.info(f"Sleepe... Rerun after {config['loop_time']} seconds")
        # 每次循环结束后等待
        await asyncio.sleep(config['loop_time'])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(main())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        task.cancel()
        loop.close()