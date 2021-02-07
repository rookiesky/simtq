from Request import Request
from bs4 import BeautifulSoup
import time
import json

request = Request()
list_url = []
cate = ''
cate_liks = []

host = 'https://community.whattoexpect.com'
post_api = 'https://www.simtq.com/wordpress_post_json_api.php?action=save'
url = 'https://community.whattoexpect.com/forums/'

temp_page_total = 0
temp_page = 1
iswhile = True

def articleList(url):
    global request, list_url, temp_page_total

    response = request.request(url=url)
    if response == False:
        return False

    soup = BeautifulSoup(response,'html.parser')
    if temp_page_total <= 0:
        number = soup.find_all('a',attrs={'class','page-link'})
        temp_page_total = int(number[-2].text)
        
    urls = soup.find_all('a',attrs={'class',"linkDiscussion"})
    list_url = [host + item.get('href') for item in urls]

def bodyFormat(body):
    try:
        for item in body.find_all('a'):
            item.attrs['rel'] = 'noopener noreferrer nofollow'
            item.attrs['target'] = '_blank'
    except:
        pass
        
    try:
        for item in body.find_all('img'):
            item.attrs['referrerpolicy'] = 'no-referrer'
            if item.attrs['data-src'] != '':
                item.attrs['src'] = item.attrs['data-src']
    except:
        pass

    return body

def crateTimeFormat(create_time):
    time_local = time.localtime(int(create_time) / 1000)
    return time.strftime("%Y-%m-%d %H:%M:%S",time_local)

def articleFormat(soup):
    title = soup.find('h1',attrs={'class','discussion-original-post__title'}).text
    create_time = soup.find('div',attrs={'class','discussion-original-post__author__updated'}).get('data-date')
    create_time = crateTimeFormat(create_time)
    author = soup.find('div',attrs={'class','discussion-original-post__author__name'}).text
    body = soup.find('div',attrs={'class','__messageContent fr-element fr-view'})
    body = bodyFormat(body)
    return {'post_author': author, 'post_title': title, 'post_content': str(body),'post_date':create_time}

def replyCommentData(item):
    author = item.find('div',attrs={'class','wte-reply__author__name'}).text
    create_time = item.find('div',attrs={'class','wte-reply__author__updated'}).get('data-date')
    create_time = crateTimeFormat(create_time)
    content = item.find('div',attrs={'class','wte-reply__content__message __messageContent fr-element fr-view'})
    content = bodyFormat(content)
    return {'author':author,'date':create_time,'content':str(content)}

def sunReplyComment(item):
    body = item.find_all('div',attrs={'class','discussion-replies__list__item__replies__reply'})
    a = []
    if body is None:
        return ''
    for item in body:
        a.append(replyCommentData(item))
    
    return a

def commnets(soup):
    all_body = soup.find_all('div',attrs={'class','discussion-replies__list__item wte-card'})
    data = []
    for item in all_body:
        a = replyCommentData(item)
        a['commn'] = sunReplyComment(item)
        data.append(a)
    
    return data
          
def article():
    global request, post_api, list_url, cate
    for url in list_url:
        response = request.request(url)
        if response == False:
            continue

        soup = BeautifulSoup(response,'html.parser')
        data = dict
        try:
            data = articleFormat(soup)
            data['replys'] = commnets(soup)
            data['post_category'] = cate
            request.requestPostJson(api=post_api,json=data)
            request.logger.info('Success,title:{}'.format(data['post_title']))
        except Exception as e:
            request.logger.error('article form error,msg:{}'.format(e))
            continue
        finally:
            soup = ''
            data = ''
            response = ''
    list_url = []

def catePage(url):
    global list_url, iswhile, temp_page
    while iswhile:
        if temp_page_total != 0 and temp_page >= temp_page_total:
            iswhile = False
        
        articleList(url + '?page={}'.format(temp_page))
        if len(list_url) <= 0:
            request.logger.error('list link empty')
            continue

        article()
        temp_page = temp_page + 1
        request.logger.info('reptile cate:{},Success! sleep 5s'.format(cate))
        time.sleep(5)

def totalPage():
    global cate_liks, cate, iswhile,list_url
    for item in cate_liks:
        cate = item['cate']
        for url in item['links']:
            if 'https:' not in url:
                url = 'https:' + url
            
            catePage(url)

            
            
def cateList():
    global url, cate_liks
    response = request.request(url=url)
    if response == False:
        exit()

    soup = BeautifulSoup(response,'html.parser')

    card = soup.find_all('div',attrs={'class','wte-site-section-card'})

    for item in card:
        cate = item.find('a',attrs={'class','wte-site-section-card__c__body__title__link'}).text
        urls = ['https:' + v.get('href') for v in item.find_all('a',attrs={'class','wte-site-section-card__c__body__links__link'})]
        urls.append(item.find('a',attrs={'class','wte-site-section-card__c__body__title__link'}).get('href'))
        cate_liks.append({'cate': cate, 'links': urls})

def main():
    cateList()
    totalPage()

if __name__ == "__main__":
    try:
        main()
        request.logger.info('whattoexpect Success all')
    except:
        pass