from Request import Request
from bs4 import BeautifulSoup
import time
import json

request = Request()
list_url = []

url = 'https://www.healthline.com/directory/topics?page='
post_api = 'https://www.simtq.com/wordpress_post_api.php?action=save'

def articleList(url):
    global request, list_url   
    response = request.request(url=url)
    if response == False:
        return False
    soup = BeautifulSoup(response,'html.parser')
    urls = soup.find_all('a',attrs={'class','css-u2j7v4'})
    list_url = [item.get('href') for item in urls]
        

def articleFormat(soup):
    title = soup.find('h1').text
    author = soup.find_all('a',attrs={'class','css-zocu4s'})[1].text
    try:
        create_date = soup.find('section',attrs={'class','css-lizeih'}).contents[1].contents[4].text
        create_date = create_date.replace('Updated on ','')
    except:
        create_date = ''
    try:
        tags = soup.find_all('a',attrs={'class','css-1ggiqr2'})
        tags = [item.text for item in tags]
        tags = ",".join(tags)
    except:
        tags = ''

    body = soup.find('article',attrs={'class','article-body'})
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
    
    try:
        body.find('div',attrs={'class','css-1cg0byz'}).extract()
    except:
        pass

    for item in body.find_all('section',attrs={'class','css-11k39sg'}):
        item.extract()

    return {'post_title': title, 'post_content': str(body), 'post_author': author, 'post_date': create_date,'tag': tags}

def article():
    global list_url, request, post_api
    for url in list_url:
        response = request.request(url)
        if response == False:
            continue

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
    global list_url, url
    for i in range(115,0,-1):
        url = url + str(i)
        articleList(url)
        if len(list_url) <= 0:
            request.logger.error('list url empty')
            continue
        article()
        request.logger.info('success,page:{},sleep 5s'.format(i))
        time.sleep(5)

if __name__ == "__main__":
    main()
    request.logger.info('Success All')