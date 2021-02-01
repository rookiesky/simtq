
cate_list = [
    {'cate':'小1','links':[
        'http://baidu',
        'https://google.com'
    ]},
    {
        'cate': '小大',
        'links': [
            'http://163.com',
            'http://qq.com',
            'http://qidian.com'
        ]
    }
]

for item in cate_list:
    print(item['cate'])
