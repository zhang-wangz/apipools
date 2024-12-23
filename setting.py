
VERSION = "1.0.0"
# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5020

# ############### database config ###################
# db connection uri
# 修改为使用sqlite，不使用redis
DB_CONN = 'sqlite:////app/data/pool.db'

# proxy table name
# 仅对使用redis和ssdb生效(目前已经无用，暂时没重新适配redis和ssdb)
TABLE_NAME = 'use_proxy'


# ###### config the proxy fetch function ######
# 该配置移动成json文件，规范每个抓取任务的间隔时间
# 可以配置day，hour，minute， second，为空代表不设置
#     "day": -1,
#     "hour": -1,
#     "minute": -1,
#     "second": -1,
# /Users/zhang-wangz/PycharmProjects/apipools/
PROXY_FETCHER_PATH = '/app/config/proxy_fetcher.json'

# ############# proxy validator #################
# 代理验证目标网站
HTTP_URL = "http://httpbin.org/ip"

HTTPS_URL = "https://httpbin.org/ip"

# 代理验证时超时时间
VERIFY_TIMEOUT = 10

# 近PROXY_CHECK_COUNT次校验中允许的最大失败次数,超过则剔除代理
MAX_FAIL_COUNT = 10

# proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
POOL_SIZE_MIN = 20

# ############# proxy attributes #################
# 是否启用代理地域属性
PROXY_REGION = True

# ############# scheduler config #################

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"
