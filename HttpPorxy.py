import requests
import logging
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import random

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)



class HttpPorxy():

    porxy_ips = dict()
    select_ip_error_number = 0
    now_ip_number = {'http':0,'https':0}

    def __init__(self,is_porxy = False):
        logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.INFO)
        self.logger = logging
        self.is_porxy = is_porxy
        if self.is_porxy == True:
            self.httpFoHttps()
        

    def userAgent(self):
        r"""随机ua头信息
        """
        ua = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0',
            'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/87.0.4280.88 Chrome/87.0.4280.88 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
            'Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.9.168 Version/11.52',
            'Opera/9.80 (Windows NT 6.1; WOW64; U; en) Presto/2.10.229 Version/11.62'
        ]
        return random.choice(ua)

    def getList(self):
        '''获取远程ip代理库
        RETURNS
        ---------------------
        data(list) OR False
        '''
        try:
            response = requests.get('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list')
            data = response.text.split('\n')
            response.close()
            return data
        except Exception as e:
            logging.error('get porxy list error,msg:{}'.format(e))
            return False

    def check(self,url,porxy):
        '''检测ip是否可用
        Parameters
        ------------------
        url : 用户测试的网址
        porxy : 用户检测的ip

        RETURNS
        ------------------
        True || False
        '''
        try:
            response = requests.get(url,proxies=porxy,timeout=3, verify=False)
            logging.info('check ip:{},url:{}'.format(url,porxy))
            if response.status_code >= 300:
                return False
            return True
        except:
            return False

    def httpFoHttps(self):
        '''区分代理类型http 获取 https
        RETURNS
        -----------------------
        {'http':[],'https':[]}
        '''
        logging.info('get porxy ip...')
        ips = self.getList()
        if ips == False:
            return False
        self.porxy_ips = {'http':[],'https':[]}
        for item in ips:
            if item == '':
                continue
            item = json.loads(item)
            if item['type'] == 'http':
                self.porxy_ips['http'].append({item['type']:item['type'] + '://' + item['host'] + ':' + str(item['port'])})
            else:
                self.porxy_ips['https'].append({item['type']:'http://' + item['host'] + ':' + str(item['port'])})
        if len(self.porxy_ips['http']) <= 0 or len(self.porxy_ips['https']) <= 0:
            logging.error('porxy list is empty')
            exit()
        
        logging.info('get porxy ip success')

    def selelctIp(self,url):
        """选择代理ip
        Parameters
        ------------------
        url 需要代理的网址，用来判断代理类型是http或者https

        RETURNS
        -------------------
        ip {}
        """
        if len(self.porxy_ips['http']) <= 0 or len(self.porxy_ips['https']) <= 0:
            self.httpFoHttps()

        if 'https' in url:
            http_type = 'https'
            u = 'https://www.baidu.com'
        else:
            http_type = 'http'
            u = 'http://www.chinatax.gov.cn/'
        
        try:
            self.porxy_ips[http_type][self.now_ip_number[http_type]]
        except IndexError:
            self.now_ip_number[http_type] = 0

        response = self.check(url=u,porxy=self.porxy_ips[http_type][self.now_ip_number[http_type]])
        if response == False:
            if self.select_ip_error_number >= 3:
                logging.error('select ip error number 3')
                exit()
            del self.porxy_ips[http_type][self.now_ip_number[http_type]]
            self.select_ip_error_number = self.select_ip_error_number + 1
            return self.selelctIp(url)

        ip = self.porxy_ips[http_type][self.now_ip_number[http_type]]
        self.now_ip_number[http_type] = self.now_ip_number[http_type] + 1
        return ip

        

    def headerFormat(self,url,headers):
        data = dict()
        head = {'user-agent': self.userAgent()}
        data['headers'] = {**head,**headers}
        data['proxies'] = {}
        if self.is_porxy:
            data['proxies'] = self.selelctIp(url)
        return data
        

    def get(self,url,headers = {}):
        '''http get 请求
        Parameters
        -------------
        url:请求的地址
        headers:http 头部信息

        Return
        ------------------
        response.text  or False
        '''
        self.select_ip_error_number = 0
        headers = self.headerFormat(url,headers)
        try:
            response = requests.get(url=url, headers = headers['headers'], proxies = headers['proxies'], verify = False, timeout = 120)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            logging.error('request get error,msg:{}'.format(e))
            return False
        finally:
            try:
                response.close()
            except:
                pass
    
    def post(self,url,data,headers = {}):
        '''http post请求
        Parameters
        ----------------
        url string 请求地址
        data dict 发送数据
        header dict  http 头部信息

        Returns
        ----------------
        response.text OR False
        '''
        self.select_ip_error_number = 0
        headers = self.headerFormat(url,headers)
        try:
            response = requests.post(url=url,data=data,headers = headers['headers'],proxies = headers['proxies'],verify = False,timeout = 120)
            return response.text
        except Exception as e:
            logging.error('http post error,msg:{}'.format(e))
            return False
        finally:
            try:
                response.close()
            except:
                pass
    
    def postJson(self,url,json,headers = {}):
        '''http post json请求
        Parameters
        ----------------
        url string 请求地址
        json dict 发送数据
        header dict  http 头部信息

        Returns
        ----------------
        response.text OR False
        '''
        self.select_ip_error_number = 0
        headers = self.headerFormat(url,headers)
        try:
            response = requests.post(url=url,json=json,headers = headers['headers'],proxies = headers['proxies'],verify = False,timeout = 120)
            return response.text
        except Exception as e:
            logging.error('http post error,msg:{}'.format(e))
            return False
        finally:
            try:
                response.close()
            except:
                pass
    