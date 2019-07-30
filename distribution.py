import pickle
from multiprocessing import Process

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from douban import Movie

# 设置matplotlib正常显示中文和负号
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def readData():
    """
    #### 功能：测试用，从本地导入MovieList
    #### 参数：None
    #### 返回：None
    """
    with open("dump.dat", "rb") as f:
        movies = pickle.load(f)
    return movies


class Distribution():
    """
    ### 电影数据分析类
    """
    @staticmethod
    def maxVotesAndMaxStarsDistribution(movies):
        """
        #### 功能：显示最多投票和最高评分电影的评分信息
        #### 参数：
                 movies:所有电影
        #### 返回：None
        """
        try:
            maxVotes = max(movies, key=lambda m: m.votes)
            maxStars = max(movies, key=lambda m: m.stars)
            name = ["5星", "4星", "3星", "2星", "1星"]
            x = np.arange(5)
            plt.figure("豆瓣分析")
            votes = plt.bar(x=x-0.2, height=maxVotes.rating, width=0.4,
                            label=maxVotes.name+"(最多投票)")
            stars = plt.bar(x=x+0.2, height=maxStars.rating, width=0.4,
                            label=maxStars.name+"(最多评分)")
            plt.xticks(x, name)
            plt.ylim(0, 100)
            for i in votes:
                plt.text(x=i.get_x()+0.05, y=i.get_height()+1,
                         s=i.get_height())
            for i in stars:
                plt.text(x=i.get_x()+0.05, y=i.get_height()+1,
                         s=i.get_height())
            plt.ylabel("投票占比（%）")
            plt.legend()
            plt.title("最多投票和最多评分的电影评价情况")
            plt.show()
        except Exception as e:
            print("maxVotesAndMaxStarsDistribution：" + repr(e))

    @staticmethod
    def typesDistribution(movies):
        """
        #### 功能：显示所有电影的前5种最多的类型
        #### 参数：
                 movies:所有电影
        #### 返回：None
        """
        allTypesCount = {
            "剧情": 0,
            "喜剧": 0,
            "动作": 0,
            "爱情": 0,
            "科幻": 0,
            "动画": 0,
            "悬疑": 0,
            "惊悚": 0,
            "恐怖": 0,
            "犯罪": 0,
            "同性": 0,
            "音乐": 0,
            "歌舞": 0,
            "传记": 0,
            "历史": 0,
            "战争": 0,
            "西部": 0,
            "奇幻": 0,
            "冒险": 0,
            "灾难": 0,
            "武侠": 0,
            "情色": 0
        }
        try:
            for m in movies:
                for t in m.types:
                    if t not in allTypesCount:
                        continue
                    allTypesCount[t] += 1
            lists = sorted(allTypesCount.items(), key=lambda x: x[1],
                           reverse=True)
            names = []
            values = []
            for i in lists[:5]:
                names.append(i[0])
                values.append(i[1])
            plt.figure("豆瓣分析")
            top5 = plt.bar(x=names, height=values, width=0.8)
            for i in top5:
                plt.text(x=i.get_x()+0.35, y=i.get_height()+0.1,
                         s=i.get_height())
            plt.title("最多类型Top 5")
            plt.xlabel("电影类型")
            plt.ylabel("电影数量（部）")
            plt.ylim(0, len(movies))
            plt.show()
        except Exception as e:
            print("typesDistribution：" + repr(e))

    @staticmethod
    def yearsDestribution(movies):
        """
        #### 功能：显示所有电影的所有年份分布信息
        #### 参数：
                 movies:所有电影
        #### 返回：None
        """
        try:
            minYear = min(movies, key=lambda x: x.year).year
            maxYear = max(movies, key=lambda x: x.year).year
            yearsCount = {}
            for i in movies:
                if i.year not in yearsCount:
                    yearsCount[i.year] = 1
                else:
                    yearsCount[i.year] += 1
            yearslist = [i.year for i in movies]
            plt.figure("豆瓣分析")
            plt.title("各年份电影数量直方图")
            plt.xlabel("电影年份（年）")
            plt.ylabel("电影数量（部）")
            plt.hist(x=yearslist, bins=maxYear-minYear+1, edgecolor="black")
            plt.show()
        except Exception as e:
            print("yearsDestribution：" + repr(e))

    @staticmethod
    def areasDestribution(movies):
        """
        #### 功能：显示所有电影的制作地区分布前5名
        #### 参数：
                 movies:所有电影
        #### 返回：None
        """
        areasCount = {
            "中国大陆": 0,
            "美国": 0,
            "香港": 0,
            "台湾": 0,
            "日本": 0,
            "韩国": 0,
            "英国": 0,
            "法国": 0,
            "德国": 0,
            "意大利": 0,
            "西班牙": 0,
            "印度": 0,
            "泰国": 0,
            "俄罗斯": 0,
            "伊朗": 0,
            "加拿大": 0,
            "澳大利亚": 0,
            "爱尔兰": 0,
            "瑞典": 0,
            "巴西": 0,
            "丹麦": 0
            }
        try:
            for m in movies:
                for t in m.areas:
                    if t not in areasCount:
                        if t == "US":
                            areasCount["美国"] += 1
                        elif t == "UK":
                            areasCount["英国"] += 1
                        else:
                            continue
                    else:
                        areasCount[t] += 1
            lists = sorted(areasCount.items(), key=lambda x: x[1],
                           reverse=True)
            areas = []
            values = []
            for i in lists[:5]:
                areas.append(i[0])
                values.append(i[1])
            plt.figure("豆瓣分析")
            top5 = plt.bar(x=areas, height=values)
            for i in top5:
                plt.text(x=i.get_x()+0.35, y=i.get_height()+0.1,
                         s=i.get_height())
            plt.ylim(0, len(movies))
            plt.title("电影数量最多的区域TOP 5")
            plt.show()
        except Exception as e:
            print("areasDestribution：" + repr(e))

    @staticmethod
    def timeDistribution(movies):
        """
        #### 功能：显示所有电影的时长分布信息（0代表时间未知）
        #### 参数：
                 movies:所有电影
        #### 返回：None
        """
        try:
            timeList = [i.time for i in movies]
            minTime = min(movies, key=lambda x: x.time).time
            maxTime = max(movies, key=lambda x: x.time).time
            plt.figure("豆瓣分析")
            plt.title("电影时间长度直方图")
            plt.xlabel("电影时间（分钟）")
            plt.ylabel("电影数量（部）")
            plt.hist(x=timeList, bins=maxTime-minTime+1, edgecolor="black")
            plt.show()
        except Exception as e:
            print("timeDistribution：" + repr(e))

    @staticmethod
    def begin(movies):
        """
        #### 功能：用多进程的方式运行所有电影分析
        #### 参数：
                 movies:电影(douban.Movies)数据列表
        #### 返回：None
        """
        pList = []
        destribute = [Distribution.maxVotesAndMaxStarsDistribution,
                      Distribution.typesDistribution,
                      Distribution.yearsDestribution,
                      Distribution.areasDestribution,
                      Distribution.timeDistribution]
        for i in destribute:
            p = Process(target=i, args=(movies,))
            p.daemon = True
            p.start()
            pList.append(p)
        for i in pList:
            i.join()


# if __name__ == "__main__":
#     movies = readData()
#     Distribution.begin(movies)
