import json
import bs4
import urllib.request as request

myURL = "https://www.ptt.cc/bbs/Gossiping/index39414.html"
writeDATA = []

def getWebData(url):
    #建立myRequest物件,附加headers訊息
    myRequest = request.Request(url, headers= {
        "cookie" : "over18=1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    })
    with request.urlopen(myRequest) as response: #附帶headers之後去URLopen
        data = response.read().decode("utf-8") #request之後讀取並解碼存在data中

    #解析
    root = bs4.BeautifulSoup(data, "html.parser") #解析html

    titles = root.find_all("div", class_ = "title")
    for title in titles:
        if title.a != None: #如果有內容就取得網址並request
            thumbs = title.find_previous_sibling('div') #取得推數
            thumbsCount = 0 
            if thumbs.span != None:
                thumbsCount = int(thumbs.span.text)

            newURL = "http://www.ptt.cc"+title.a["href"]
            newRequest = request.Request(newURL, headers= {
                "cookie" : "over18=1",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            })
            with request.urlopen(newRequest) as response: #附帶headers之後去URLopen
                Data = response.read().decode("utf-8") #request之後讀取並解碼存在Data中

            newPage = bs4.BeautifulSoup(Data, "html.parser") #解析html
            topINFO = newPage.find_all("span", class_="article-meta-value") #關於 標題,作者,看版,日期的訊息
            article = newPage.find("div", id="main-container") #內文的訊息
            replies = newPage.find_all("div", class_ = "push") #留言的訊息
            if len(topINFO) == 0:
                continue
            dic = {}
            dic["作者"] = topINFO[0].text
            dic["看板"] = topINFO[1].text
            dic["標題"] = topINFO[2].text
            dic["日期"] = topINFO[3].text
            dic["推數"] = thumbsCount
            allText = article.text
            splitText = allText.split("--\n※ 發信站:", 1)
            dic["內容"] = splitText[0].split("\n",2)[2]
            messagesObjs = []
            for reply in replies:
                mesObj = {}
                infos = reply.find_all("span")
                mesObj["推噓"] = infos[0].text[0]
                mesObj["用戶"] = infos[1].text
                mesObj["內容"] = infos[2].text[2:]
                mesObj["時間"] = infos[3].text[1:].strip()
                messagesObjs.append(mesObj)
            if len(messagesObjs) > 0:
                dic["留言"] = messagesObjs
            else:
                dic["留言"] = []
            writeDATA.append(dic)   

    lastPageLink = root.find("a", string = "‹ 上頁")
    return ("https://www.ptt.cc/" + lastPageLink["href"])


counter = 1
while counter < 3:
    myURL = getWebData(myURL)
    print("page_"+str(counter)+" finished")
    counter += 1

#將內容寫入json
with open("data.json", mode="w", encoding="utf-8") as myFile:
    json.dump(writeDATA, myFile, indent=4, ensure_ascii=False)