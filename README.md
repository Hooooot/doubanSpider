# 豆瓣爬虫
## 使用方法：
> 运行main.py即可进入主界面

> 功能：抓取豆瓣电影各分类评分前N部，并分析电影所属区域、电影时间长度、电影最多评论、最高评分、电影年代分布、电影类型分布等信息

### 版本说明：
#### V1.1.0：
> 添加多线（进）程运行，提高效率。部分界面优化

#### V1.0.0：
> 首次发布

## 环境：

| 语言       | 版本   |  下载  |
| --------  | :-----:  |  :----:  |
| `Python`  |  3.7.4 64bit  | [下载](https://www.python.org/downloads/release/python-374/ "下载") |


| 第三方库    | 版本   |  安装命令  |
| --------   | :-----:  |  :----:  |
| `requests`  |  2.22.0  | [pip install requests](https://pypi.org/project/requests/ "pip install requests") |
| `matplotlib` |  3.0.3  | [pip install matplotlib](https://pypi.org/project/matplotlib/ "pip install matplotlib") |
| `PyQt5` | 5.11.3 | [pip install PyQt5](https://pypi.org/project/PyQt5/ "pip install PyQt5") |
| `beautifulsoup4` | 4.8.0 | [pip install beautifulsoup4](https://pypi.org/project/beautifulsoup4/ "pip install beautifulsoup4") |
| `numpy` |  1.16.3  | [pip install numpy](https://pypi.org/project/numpy/ "pip install numpy")  |

## 目录
- 
    - main.py
    - douban.py
    - distribution.py
    - dump.dat
    - test.py
    - README.md
> 文件说明： <br/>
&nbsp;&nbsp;main.py：程序主窗口文件，程序入口<br/>
&nbsp;&nbsp;douban.py：豆瓣爬虫，用于获取电影信息<br/>
&nbsp;&nbsp;distribution.py：用于分析电影数据<br/>
&nbsp;&nbsp;dump.dat：电影信息序列化文件（仅调试时用）<br/>
&nbsp;&nbsp;test.py：调试时用于测试UI功能
    
