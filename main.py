from adguardhome import AdGuardHome
from typing import Union

import pandas as pd
import asyncio
import subprocess
import toml
import os
import logging
import requests
import re


def init_logger() -> logging.Logger:
    """初始化日志记录器

    Returns: 
        logging.Logger: 返回一个配置好的日志记录器 
    """ 
    # 配置日志级别
    logging.basicConfig(level=logging.INFO)
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


async def check_and_update_domains(domain, best_ip, adguard):
    """
    检查并更新域名重写规则

    Args:
        domain (str): 要检查和更新的域名
        best_ip (str): 最佳 IP 地址
        adguard (AdGuardHome): AdGuardHome 客户端实例
    """
    # 获取当前 AdGuardHome 的域名重写列表
    adguard_domain_list = await adguard.request(uri='rewrite/list')
    
    # 检查域名是否在重写列表中，如果存在则进行更新，否则进行添加
    result = check_domain(domain=domain, adguard_domain_list=adguard_domain_list)
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
    else:
        await adguard.request(uri='rewrite/add', method='POST', json_data=put_data)


def check_connect(test_url:str, max_delay:float, logger:logging.Logger) -> bool:
    """检查连接是否可用并且响应时间是否在指定的最大延迟范围内

    Args:
        test_url (str): 要测试的URL
        max_delay (float): 最大延迟时间（秒）

    Returns:
        bool: 如果连接可用并且响应时间小于最大延迟时间，则返回True；否则返回False
    """
    test_url = re.match(r'(https?://[^/]+)', test_url).group(1)
    res = requests.get(test_url)
    if res.status_code == 200 and res.elapsed.total_seconds() < max_delay:
        logger.info(f"Delay is {res.elapsed.total_seconds()} seconds")
        return True
    else:
        return False


async def main():
    """
    主函数，用于执行主要逻辑
    """
    config = toml.load('config.toml')
    logger = init_logger()

    main_path = '/CloudflareSpeedTest/'
    sub_path = 'CloudflareSpeedTest/'
    if os.path.exists(main_path):
        os.chdir(main_path)
    else:
        os.chdir(sub_path)

    while True:
        logger.info("Start check ip")

        # 运行 CloudflareST 程序
        result = subprocess.run(['./CloudflareST','-httping', '-url', config['test_url'], '-t', config['test_ping_count'], '-tlr', config['test_packet_loss']], \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("check complete")
        logger.info(result.stdout)  # 将子进程的标准输出添加到日志
        logger.debug(result.stderr)  # 将子进程的错误输出添加到日志

        try: 
            # 读取并删除 result.csv 文件
            best_ip = pd.read_csv('result.csv').loc[0, 'IP 地址']
            os.remove('result.csv')

            async with AdGuardHome(host=config['ad_guard_home_url'],
                                port=config['ad_guard_home_port'],
                                username=config['ad_guard_home_username'],
                                password=config['ad_guard_home_passwd']) as adguard:
                tasks = []
                for domain in config['domains']:
                    # 创建并发任务来检查和更新域名重写规则
                    task = asyncio.create_task(check_and_update_domains(domain, best_ip, adguard))
                    tasks.append(task)
                await asyncio.gather(*tasks)

                logger.info(f"Update Cloudflare IP is {best_ip}")

            while check_connect(config['test_url'], config['test_max_delay'], logger):
                await asyncio.sleep(60)

        except (FileNotFoundError, FileExistsError) as e:
            logger.warning(str(e))
            continue


if __name__ == "__main__":
    asyncio.run(main())