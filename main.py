from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import asyncio
from graph_data_BS.graph_data import BS_RusNames
from exceptions import InvalidPointsException

class RouteMaker:


    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=700,900')

    @staticmethod
    async def l_lonan(from_point_rus, to_point_rus):
        from_point, to_point = BS_RusNames.get(from_point_rus, None), BS_RusNames.get(to_point_rus, None)
        if not from_point:
            raise InvalidPointsException("начальная точка задана неправильно или не существует.")
        if not to_point:
            raise InvalidPointsException('конечная точка задана неправильно или не существует.')
        driver = webdriver.Chrome(options=RouteMaker.options)
        driver.get('https://mospolynavigation.github.io/clientNavigation/')
        driver.find_elements(By.CLASS_NAME, 'button-minus')[0].click()
        await asyncio.sleep(0.5)
        driver.execute_script(f'return startNewRoute("{from_point}", "{to_point}");')
        await asyncio.sleep(1)
        imgs = []
        older_status =  driver.find_elements(By.TAG_NAME, 'g')[0].get_attribute('id')
        newer_status = None
        while True:
            imgs.append(driver.get_screenshot_as_png())
            driver.execute_script('return nextStep();')
            await asyncio.sleep(1)
            newer_status = driver.find_elements(By.TAG_NAME, 'g')[0].get_attribute('id')
            if newer_status == older_status:
                break
            older_status = newer_status
        driver.quit()
        return imgs

async def main():
    t1 = datetime.datetime.now()
    tasks = []
    tasks.append(asyncio.create_task(RouteMaker.l_lonan('А102', 'А405')))
    tasks.append(asyncio.create_task(RouteMaker.l_lonan('Н212', 'Н508')))
    tasks.append(asyncio.create_task(RouteMaker.l_lonan('В104', 'А108')))
    res = []
    for task in tasks:
        try:
            task_ans = await task
            res.append(task_ans)
        except InvalidPointsException:
            print('One of tasks has failed.')
    for i in range(len(res)):
        for j in range(len(res[i])):
            f = open(f'folder{i}/{j}.png', 'wb')
            f.write(res[i][j])
            f.close()
    print(f'Programm took {datetime.datetime.now() - t1} seconds to execute')



if __name__ == "__main__":
    asyncio.run(main())
