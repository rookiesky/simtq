from Request import Request
from bs4 import BeautifulSoup
import time
import json

request = Request()
list_url = []

url = 'https://www.childrens.com/wps/FusionService/api/public/query/Childrens/Childrens?rows=12&fq=%7B!tag%3DmainCategory_s%7DmainCategory_s:%22articles%22&sort=desc'
post_api = 'https://www.simtq.com/wordpress_post_api.php?action=save'


def articleList(url):
    global request, list_url

    response = request.request(url=url)
    if response == False:
        exit()
    soup = json.loads(response)
    docs = soup['response']['docs']
    for item in docs:
        list_url.append(item['url'])
    
    
    


def articleFormat(soup):
    title = soup.find('h1',attrs={'itemprop':'headline name'}).text
   
    author = soup.find('span',attrs={'itemprop':'author'}).text
    try:
        create_time = soup.find('span',attrs={'itemprop':'DatePublished'}).text
    except:
        create_time = ''
    
    body = soup.find('div',attrs={'itemprop':'articleBody'})
    del body.contents[-6:-1]

    try:
        tags = soup.find('p',attrs={'itemprop':'about subjectOf'}).next
    except:
        tags = ''

    try:
        for item in body.find_all('a'):
            item.attrs['href'] = '/'
            item.attrs['rel'] = 'noopener noreferrer nofollow'
            item.attrs['target'] = '_blank'
    except:
        pass
    
    try:
        for item in body.find_all('img'):
            item.attrs['referrerpolicy'] = 'no-referrer'
    except:
        pass
    
    return {'post_title': title, 'post_content': str(body), 'post_author': author, 'post_date': create_time,'tag': tags}

def article():
    global list_url, request, post_api
    for url in list_url:
        response = request.request(url)
        if response == False:
            exit()

        soup = BeautifulSoup(response,'html.parser')
        try:
            data = articleFormat(soup)
            data['post_category'] = 3
            request.requestPost(wordpress_api=post_api,data=data)
            request.logger.info('Success!Post title:{}'.format(data['post_title']))
        except Exception as e:
            request.logger.error('article format error,msg:{}'.format(e))
            continue
        finally:
            soup = ''
            response = ''
    list_url = []

def main():
    global url,request, list_url
    articleList(url)
    if len(list_url) <= 0:
        exit()
    article()
    request.logger.info('reptile childrens Success!')


if __name__ == "__main__":
    try:
        main()
    except:
        pass

#return {'post_title': title, 'post_excerpt': excerpt, 'tag': tages, 'post_content': content, 'post_author': author, 'post_date': create_time, 'post_category': 2}