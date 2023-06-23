import requests
import json
import time
datas = []
requests.packages.urllib3.disable_warnings()
# 参数
token = ''
# 楼栋ID
budingID = ''
# 电表地址
comAddress= ''
# 在浏览器控制台（F12）——网络——XHR中找到token和buildingID和comAddress#
#-----为空则不推送-----#
bark_token = ''
#-------------------------不需要修改---------------------------------------------------#
# 查询URL
url = 'https://cz.gdou.edu.cn//APIXCX/app/xcx/meterinfo/' \
      'getMeterStatus1?token='+token+'buildingID='+budingID
# 刷新电表url
refesh_url = 'https://cz.gdou.edu.cn//APIXCX/ypt/app/message/readMeter?buildingID='\
             +budingID+'&comAddress='+comAddress+'&dataItemID=00057&userName=ass'
#------------------------------------------------------------------------------------#
# 发送推送通知
def send_push_notification(topic,content):
    if bark_token == '':
        print("Bark token is empty, push notification is not sent.")
        return
    else:
        url = "https://api.day.app/"+bark_token+'/' + topic + '/' + content + '?icon=https://i.imgloc.com/2023/06/23/VI33xc.md.png'
        #print(url)
        response = requests.get(url)
        if response.status_code == 200:
            #print("Push notification sent successfully!")
            pass
        else:
            print("Failed to send push notification. Status code:"+ str(response.status_code))
        return response.status_code
# 发送请求
def send_request(url):
    global datas
    try:
        response = requests.get(url,verify=False)
        if response.status_code == 200:
            #print("Request sent successfully!")
            data = response.text
            # 解析JSON数据
            data_dict = json.loads(data)
            # 提取参数
            parameters = data_dict['data'][0]
            # customer_name = data_dict['customerName']
            # 输出参数
            for key, value in parameters.items():
                datas.append(f"{key}: {value}")
        else:
            print("Failed to send request. Status code:"+ str(response.status_code))
            datas = []
    except:
        print("Failed to send request. Please check your network connection.")
        datas = []
# 刷新电表
def refesh_meter(refesh_url):
    try:
        response = requests.get(refesh_url,verify=False)
        if response.status_code == 200:
            #print("Refresh meter successfully!")
            pass
        else:
            print("Failed to refresh meter. Status code:"+ str(response.status_code))
    except:
        print("Failed to refresh meter. Please check your network connection.")

if __name__ == '__main__':
    if datas == []:
        refesh_meter(refesh_url)
        time.sleep(3)
        send_request(url)
        if datas == []:
            send_push_notification('电费查询失败','请检查校园网连接')
            exit()
        else:
            datas[8] = datas[8].replace('-','');datas[9] = datas[9].split(':',1)[1]
            print('电费查询成功');print(datas[3]);print(datas[6]);print(datas[8]);print(datas[9])
            send_push_notification('电费查询成功','\n'+datas[3]+'\n'+datas[6]+'\n'+datas[8]+'\n'+datas[9])
