# https://stackoverflow.com/questions/59503825/django-async-to-sync-vs-asyncio-run
# 做了点修改
from asgiref.sync import async_to_sync
import time,asyncio
async def async_sleep(t0):
    await asyncio.sleep(1)
    print(time.time() - t0)

async_to_sync_sleep = lambda f_n_l=False: async_to_sync(async_sleep,force_new_loop=f_n_l)
def main():
    print('\nasync_to_sync')
    t0 = time.time()
    async_to_sync_sleep(f_n_l=True)(t0)
    async_to_sync_sleep(f_n_l=True)(t0)
    


main()