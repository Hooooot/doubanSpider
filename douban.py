import re
from multiprocessing import Process, Queue
from threading import Lock, Thread
import numpy as np
import requests
from bs4 import BeautifulSoup

# 全局线程锁
threadLock = Lock()


class Movie:
    def __init__(self, name, stars, votes, rating,
                 areas, year, types, time, url):
        """
        #### Movie(name, stars, votes, rating, areas, year, types, time, url)
        #### 构造函数参数说明：
              name:电影名(str->str)
              stars:评分(str->float)
              votes:投票人数(str->int)
              rating:评分情况(5星开始,54321)(list->list)
              area:地区(list->list)
              year:上映年份(str->int)
              types:电影类型(list->list)
              time:影片时间(str->int)
              url:电影豆瓣链接(str-str)
        """
        self.name = name
        self.stars = float(stars)
        self.votes = int(votes)
        self.rating = [float(i.rstrip("%")) for i in rating]
        self.areas = areas
        self.year = int(year)
        self.types = types
        self.time = int(time)
        self.url = url

    def __str__(self):
        return "电影名：" + self.name + "\t评分：" + str(self.stars) + "\t投票人数：" +\
               str(self.votes) + "\t投票分布：" + str(self.rating) + "\t地区：" +\
               str(self.areas) + "\t年份：" + str(self.year) + "\t类型：" +\
               str(self.types) + "\t时长：" + str(self.time) + "\t地址：" + self.url

    def __iter__(self):
        return [self.name, str(self.stars), str(self.votes), str(self.rating),
                str(self.areas), str(self.year), str(self.types),
                str(self.time), self.url]

    def __getitem__(self, n):
        return self.__iter__()[n]


class Spider:
    def __init__(self, params, amount, status=None):
        """
        #### Spider(params, amount)
        #### 参数：
                 params:爬虫的请求参数
                 amount:需要爬取的电影数量
                 status:若为单线程运行，则为主窗口状态栏，可以通过emit()显示信息
                        否则为None，无意义
        """
        self.url = "https://movie.douban.com/j/new_search_subjects"
        # 任务总数
        self.amount = amount
        # 爬虫请求参数
        self.params = params
        # 单线程运行时，是主窗口状态栏，如果开启并发，则始终为None
        self.status = status
        self.head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\
537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        # 存储爬到的movie豆瓣链接
        self.movieUrls = []
        # 存储爬到的movie信息
        self.movies = []
        # 进程通信队列
        self.queue = Queue()

    def GetMovies(self, multiThread=False):
        """
        #### 功能：获取符合条件的电影URL，并将URLs保存到self.movieUrls
        #### 参数：
                 multiThread:是否使用多线程,默认禁用
        #### 返回：None
        """
        # 需要的线程数，每个线程20个任务
        # 如果禁用多线程，则该变量代表需要运行的次数
        need = self.amount // 20
        # 剩余的任务数
        left = self.amount % 20
        if multiThread:
            # 使用多线程
            threadList = []
            for i in range(need):
                t = Thread(target=self.GetMovieUrlsThread, args=(i*20,))
                threadList.append(t)
                t.start()
            # 处理剩余的任务数
            if left != 0:
                t = Thread(target=self.GetMovieUrlsThread,
                           args=(self.amount-left, left), name="left")
                t.start()
                t.join()
                # self.status.emit("正在获取电影链接：（%d/%d）" % (20, self.amount))
            for i, t in enumerate(threadList):
                t.join()
                # self.status.emit("正在获取电影链接：（%d/%d）" %
                #                  ((i+1)*20, self.amount))
        else:
            # 不使用多线程
            for i in range(need):
                self.GetMovieUrlsThread(i*20)
                self.status.emit("正在获取电影链接：（%d/%d）" % (i*20, self.amount))
            if left != 0:
                self.GetMovieUrlsThread(self.amount-left, left)
                self.status.emit("正在获取电影链接：（%d/%d）" %
                                 (self.amount, self.amount))

    def GetMovieUrlsThread(self, start, amount=20):
        """
        #### 功能：获取符合条件的电影URL任务的线程，将URLs保存到self.movieUrls
        #### 参数：
                 start:起点
                 amount默认20
        #### 返回：None
        """
        para = dict(self.params)
        para["start"] = start
        json = requests.get(url=self.url, headers=self.head,
                            params=para, timeout=5)
        data = json.json()["data"]
        if len(data) == 0:
            return
        if amount != 20:
            for i, d in enumerate(data):
                if i >= amount:
                    return
                self.movieUrls.append(d["url"])
        else:
            for d in data:
                threadLock.acquire()
                self.movieUrls.append(d["url"])
                threadLock.release()

    def GetMovieInfos(self, multiProcess=False):
        """
        #### 功能：通过self.moviesUrls来获取电影的详细信息,并将结果保存到self.movies中
        #### 参数：
                 multiProcess:是否开启多进程,默认不开启
        #### 返回：None
        """
        if multiProcess is False:
            # 不使用多进程
            self.GetMovieInfosProcess(self.movieUrls)
            return
        # 使用多进程
        urls = np.array(self.movieUrls)
        runningSize = Queue()
        length = len(urls)
        need = length // 8
        left = length % 8
        processList = []
        if left == 0 or need == 0:
            if left == 0:
                urls = urls.reshape(8, -1)
                for n in urls:
                    p = Process(target=self.GetMovieInfosProcess,
                                args=(n, self.queue, runningSize, True))
                    p.daemon = True
                    processList.append(p)
                    runningSize.put(p.pid)
                    p.start()
            else:
                p = Process(target=self.GetMovieInfosProcess,
                            args=(urls, self.queue, runningSize, True))
                p.daemon = True
                processList.append(p)
                runningSize.put(p.pid)
                p.start()
        else:
            n_urls = urls[:-left]
            n_urls.resize(8, need)
            l_urls = urls[-left:]
            for n in n_urls:
                p = Process(target=self.GetMovieInfosProcess,
                            args=(n, self.queue, runningSize, True))
                processList.append(p)
                runningSize.put(p.pid)
                p.start()
            p_l = Process(target=self.GetMovieInfosProcess,
                          args=(l_urls, self.queue, runningSize, True))
            runningSize.put(p_l.pid)
            p_l.daemon = True
            p_l.start()
        # count = 1
        while not runningSize.empty() or not self.queue.empty():
            self.movies.append(self.queue.get())
            # self.status.emit("正在获取电影详细信息：（%d/%d）" % (count, self.amount))
            # count += 1

    def GetMovieInfosProcess(self, movieUrls, queue=None,
                             runningSize=None, multiProcess=False):
        """
        #### 功能：执行获取电影的详细信息任务的进程,并将结果保存到self.movies中
        #### 参数：
                 movieUrls:电影信息的链接
                 queue:队列，用于进程间通信
                 runningSize:队列，每新建一个子进程都会put进pid，子进程结束时会get，为空时主进程才会有可能结束
                 multiProcess:是否为子进程，默认为否，此时queue、runningSize均无效
        #### 返回：None
        """
        for i, movieUrl in enumerate(movieUrls):
            try:
                page = requests.get(movieUrl, headers=self.head, timeout=5)
                html = BeautifulSoup(page.text, "html.parser")
                name = html.find("span", property="v:itemreviewed")
                if name is None:
                    print("name为空：" + movieUrl)
                    continue
                else:
                    name = name.text
                stars = html.find("strong", class_="ll rating_num").text
                v = html.find("span", property="v:votes")
                if v is None:
                    votes = "0"
                    stars = "0"
                else:
                    votes = v.text
                t = html.find_all("span", property="v:genre")
                types = [i.text for i in t]
                info = html.find("div", id="info")
                a = re.search(r"制片国家/地区: (.*)", info.text)
                if a is None:
                    print("制片国家/地区问题" + movieUrl)
                    continue
                else:
                    a = a.group(1)
                areas = a.split(" / ")
                ti = html.find("span", property="v:runtime")
                if ti is None:
                    tim = re.search(r"片长: ([0-9]*).*", info.text)
                    if tim is None:
                        time = "0"
                    else:
                        time = tim.group(1)
                else:
                    time = ti["content"]
                y = html.find("span", class_="year")
                if y is not None:
                    y = y.text
                else:
                    y = re.search(r"上映日期: ([0-9]{4}).*", info.text).group(1)
                year = y.lstrip("(").rstrip(")")
                r = html.find_all("span", class_="rating_per")
                rating = [i.text for i in r]  # 5星开始 54321
                movie = Movie(name, stars, votes,
                              rating, areas, year, types, time, movieUrl)
                if multiProcess:
                    queue.put(movie)
                else:
                    self.status.emit("正在获取电影详细信息：（%d/%d）" % (i+1, self.amount))
                    self.movies.append(movie)
            except Exception as e:
                print(movieUrl + "  " + repr(e))
        if multiProcess:
            runningSize.get()

    @staticmethod
    def begin(params, amount, status, concurrent=False):
        """
        #### 功能：开始运行爬虫
        #### 参数：
                 params:爬虫的请求参数
                 amount:需要爬取的电影数量
                 status:状态信号，emit()到主窗口状态栏
                 concurrent:是否并发执行，默认否，此时GetMovies()和GetMovieInfos()都将使用单线(进)程执行
        #### 返回：已爬完的爬虫(douban.Spider)实例
        """
        if concurrent:
            spider = Spider(params, amount, None)
        else:
            spider = Spider(params, amount, status)
        status.emit("正在获取电影链接......")
        spider.GetMovies(concurrent)
        status.emit("正在获取电影详细信息......")
        spider.GetMovieInfos(concurrent)
        status.emit("已完成！")
        return spider


# def show(s):
#     print(s)


# if __name__ == "__main__":
#     params = {
#             "sort": "S",
#             "range": "0,10",
#             "tags": "电影",
#             "start": 0,
#             "genres": "喜剧",
#             "countries": "中国大陆",
#             "year_range": "2000,2009"
#         }
#     spider = Spider.begin(params, 2, "None", True)
#     print(spider.movies)
