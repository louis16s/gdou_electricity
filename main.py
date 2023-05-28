import time,os,re
import cryptocode
import msvcrt
from configparser import ConfigParser
from datetime import datetime

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

from playwright.sync_api import Playwright, sync_playwright, expect

file100 = 'bill.ini'
version_info = '1.0'

def pwd_input():  # 密码
    import msvcrt
    chars = []
    while True:
        try:
            newChar = msvcrt.getch().decode(encoding="utf-8")
        except:
            return input("你很可能不是在cmd命令行下运行，密码输入将不能隐藏:")
        if newChar in '\r\n':  # 如果是换行，则输入结束
            break
        elif newChar == '\b':  # 如果是退格，则删除密码末尾一位并且删除一个星号
            if chars:
                del chars[-1]
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格
                msvcrt.putch(' '.encode(encoding='utf-8'))  # 输出一个空格覆盖原来的星号
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格准备接受新的输入
        else:
            chars.append(newChar)
            msvcrt.putch('*'.encode(encoding='utf-8'))  # 显示为星号
    return (''.join(chars))

def printer(content,t=True,style="yellow"):  # 彩色输出
    console = Console()
    if t == True:
        time1 = datetime.now().strftime('[%Y-%m-%d][%H:%M:%S]')
        console.print(time1, end='')
    console.print(content, style=style)

def input_types(prompt,types,lens=0):
    text = 0
    while True:
        try:
            text = input()
        except ValueError:
            printer(prompt,style="green")
            continue
        if lens == 0:
            pattern = re.compile(r'海')
            match = re.search(pattern, str(text))
            if match and len(str(text)) == 2:
                break
            else:
                printer(prompt,style="yellow")
        else:
            if re.match(types, str(text)) and len(str(text)) == int(lens):
                break
            else:
                printer(prompt,style="bold red")
    return text

def file1():  # 文件读写  
    global name, account, password, domi0, domi1, domi2
    console = Console()
    if os.path.exists(file100):  # 文件存在检测
        # printer('file existed')
        cf = ConfigParser()
        cf.read(file100)
        version = cf.get('parm', 'ver')
        if version < version_info:
            os.remove(file100)
            with console.screen(style="bold white on red") as screen:
                text = Align.center("[blink]配置文件\n版本过低\n自动删除[/blink]", vertical="middle")
                screen.update(Panel(text))
                time.sleep(5)
            file1()
        # main
        name = cf.get('main', 'nam')
        account = cf.get('main', 'uid')
        password = cf.get('main', 'pwd')
        # parm
        domi0 = cf.get('parm', 'domi0')
        domi1 = cf.get('parm', 'domi1')
        domi2 = cf.get('parm', 'domi2')


        # return name, account, password, domi0, domi1, domi2
    else:
        printer('config file not fund')
        os.system('mode con cols=44 lines=16')
        printer('*'*19+' GDOU '+'*'*19,style="bold red",t=False)
        printer('请如实填写,否则无法查询,输入后按回车',t=False)
        printer('输入你的姓名')
        name = input()
        printer('输入你的学工号')
        account = input_types('重新输入你的学工号',r'^[0-9]*$',12)

        printer('输入登陆密码')
        password = pwd_input()
        print(' ')

        printer('输入大院【海*】')
        domi0 = input_types('重新输入大院【海*】',r'^海',0)
        printer('输入楼栋【A|B|C】')
        domi1 = input_types('重新输入楼栋【A|B|C】',r'^[A-C]$',1)
        printer('输入房号【502】')
        domi2 = input_types('重新输入房号【502】',r'^[0-9]*$',3)

        t0 = '\n'
        password = cryptocode.encrypt(password, 'louis16s')  # 加密

        with open(file100, "w") as file:
            file.write(
                '[main]' + t0 +
                'nam = ' + str(name) + t0 +
                'uid = ' + str(account) + t0 +
                'pwd = ' + str(password) + t0 +
                '[parm]' + t0 +
                'domi0 = ' + str(domi0) + t0 +
                'domi1 = ' + str(domi1) + t0 +
                'domi2 = ' + str(domi2) + t0 +
                'ver = ' + version_info + t0)
            file.close()
        for step in track(range(100), description="Writing..."):
            time.sleep(0.01)
        printer('config is generated')

    password = cryptocode.decrypt(password, 'louis16s')  # 解密

    return name,account, password, domi0, domi1, domi2

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(channel="msedge", headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://cz.gdou.edu.cn/#/gdhydxlogin")
    name, account, password, domi0, domi1, domi2 = file1()
    temp1 = domi0+ domi1
    temp2 = int(domi2)
    temp2 //= 100
    temp2 = str(temp2)+'楼'
    page.get_by_role("textbox").first.fill(name)
    page.get_by_role("textbox").nth(1).fill(account)
    page.get_by_role("textbox").nth(2).fill(str(password))
    page.get_by_text("确定").click()
    #page.get_by_placeholder("请选择").first.click()
    #page.get_by_role("listitem").filter(has_text="湖光校区").click()
    page.get_by_placeholder("请选择").nth(1).click()
    page.get_by_role("listitem").filter(has_text=temp1).click()
    page.get_by_placeholder("请选择").nth(2).click()
    page.get_by_role("listitem").filter(has_text=temp2).click()
    page.get_by_placeholder("请选择").nth(3).click()
    page.get_by_role("listitem").filter(has_text=domi2).click()
    page.get_by_text("确定").click()
    page.locator("div").filter(has_text="电表").nth(3).click()
    target_element = page.query_selector('#app > div > div.content > div.top_detail > div.number > div.left')
    if target_element:
        printer(target_element.inner_text().split('\n')[0]+' '+target_element.inner_text().split('\n')[1])
    else:
        printer('查询网址好像出现了一些问题',style="bold red",t=False)

    #printer(page.text_content(selector="#app > div > div.content > div.top_detail > div.number > div.left"))
    printer('总用电量(kWh) ' + str(page.text_content(selector="#app > div > div.content > div.bottom_detail > div:nth-child(1) > div.number")))
    #page.screenshot(path="screenshot.png", full_page=True)
    page.get_by_text("月用电账单").click()
    target_element = page.query_selector('#app > div > div.content > div.list > div:nth-child(4) > div.number > span')
    if target_element:
        printer('当月电费(元）'+' '+str(target_element.inner_text()))
        #print(type(target_element.inner_text()))
    else:
        printer('查询网址好像出现了一些问题', style="bold red", t=False)
    page.locator("img").click()

    # 充值功能
    printer('是否充值?(回车确认)',t=False)
    if input() == '':
        page.get_by_placeholder("请输入充值金额").fill(input('请输入充值金额:'))
        page.get_by_placeholder("请输入支付密码").fill(input('请输入支付密码:'))
        page.get_by_text("确定充值").click()
        page.get_by_role("button", name="确定").click()
        time.sleep(10)
    else:
        pass
    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    printer('script started')
    temp = file1()
    if os.path.exists(file100):
        os.system('mode con cols=45 lines=9')
        printer('电费管理 version ' + version_info)
        printer('查询账号:'+temp[1])
        printer('查询房间:'+temp[3]+temp[4]+temp[5])

        try:
            run(playwright)
        except:
            printer('script error')
            exit(1)
