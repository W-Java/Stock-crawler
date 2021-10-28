import re
import tushare as ts
import mplfinance as mpf
from pylab import mpl
import wx
import pandas as pd
from selenium import webdriver
from db_connect import InsertData


class Frame2(wx.Frame):
    num = ''
    def __init__(self):
        super().__init__(parent=None, title='股票爬虫', size=(395, 180))
        self.Centre()  # 设置窗口居中

        #分割窗口
        splitter = wx.SplitterWindow(self, -1)
        #创建左右面板
        leftpanel = wx.Panel(splitter)
        rightpanel = wx.Panel(splitter)
        splitter.SplitVertically(leftpanel, rightpanel, 100)
        splitter.SetMinimumPaneSize(80)

        button = wx.Button(rightpanel, label = '确定')
        self.tc = wx.TextCtrl(rightpanel, -1, '', pos=(35, 80), size=(150, -1), name='TC', style=wx.TE_CENTER)

        font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD, False, '微软雅黑')
        font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, True, '微软雅黑')
        list2 = ['深证', '上证', '创业板']
        lb2 = wx.ListBox(leftpanel, -1, choices=list2, style=wx.LB_SINGLE)
        lb2.SetFont(font1)
        self.Bind(wx.EVT_LISTBOX, self.on_listbox, lb2)

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(lb2, 1, flag=wx.ALL | wx.EXPAND, border=5)
        leftpanel.SetSizer(vbox1)

        vbox2 = wx.BoxSizer(wx.VERTICAL)
        self.content = wx.StaticText(rightpanel, label='请选择您想要爬取的股票分类')
        self.content.SetFont(font2)
        vbox2.Add(self.content, 1, flag=wx.ALL | wx.EXPAND, border=10)
        vbox2.Add(button, 1, flag = wx.NORMAL | wx.NORMAL, border = 70)
        rightpanel.SetSizer(vbox2)

        button.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)  # 按钮左键弹起

    def OnLeftUp(self, evt):
        '''左键弹起事件函数'''
        global num
        num = self.tc.GetValue()
        self.Destroy()

# '''
# 开始爬数据
# '''

        number = num
        # chromedriver的安装位置
        driver = webdriver.Chrome(executable_path=r'D:\chromedriver.exe')
        # 打开贵州茅台的历史行情表对应的网页
        driver.get('https://q.stock.sohu.com/cn/' + number + '/lshq.shtml')
        em = driver.find_element_by_id('BIZ_hq_historySearch')
        trtext = em.text
        driver.quit()
# '''
# 正则表达式
# '''
        def parse_one_page(html):
            pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?src="(.*?)".*?name"><a'
                                 + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                                 + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
            items = re.findall(pattern, html)
            # print(items)
            for item in items:
                yield {
                    'index': item[0],
                    'image': item[1],
                    'title': item[2],
                    'actor': item[3].strip()[3:],
                    'time': item[4].strip()[5:],
                    'score': item[5] + item[6]
                }
###数据处理
        tx = trtext.split('\n')
        wholedata = {}  # 总计的数据//一行
        data = []  # 存储数据

        v = 0
        while v < len(tx):
            if v == 0:  # 第一行
                v += 1
                continue
            elif v == 1:  # 第二行
                tr = tx[v].split(' ')

                wholedata['date'] = (tr[1].replace('至', '~')).replace('2021', '21')
                wholedata['updown_e'] = tr[2]
                wholedata['updown_f'] = tr[3].replace('%', '')
                wholedata['lowest'] = tr[4]
                wholedata['highest'] = tr[5]
                wholedata['deal_num'] = tr[6]
                wholedata['deal_money'] = tr[7]
                wholedata['change_rate'] = tr[8].replace('%', '')
            else:  # 第三行开始
                trr = tx[v].split(' ')
                data_eve = {}
                data_eve['date'] = trr[0].replace('-', '/')
                data_eve['open'] = trr[1]
                data_eve['close'] = trr[2]
                data_eve['updown_e'] = trr[3]
                data_eve['updown_f'] = trr[4].replace('%', '')
                data_eve['lowest'] = trr[5]
                data_eve['highest'] = trr[6]
                data_eve['deal_num'] = trr[7]
                data_eve['deal_money'] = trr[8]
                data_eve['change_rate'] = trr[9].replace('%', '')

                data.append(data_eve)

            v += 1


        # print(wholedata)
        # print(data)

# '''
# 生成csv文件
# '''

        name = ['data', 'open', 'close', 'updown_e', 'updown_f', 'lowest', 'highest', 'deal_num', 'deal_money', 'change_rate']
        test = pd.DataFrame(columns=name, data=data)
        test.to_csv('D:\\桌面\\test.csv', index=False)

# '''
# 生成k线图
# '''

        # pd.set_option()就是pycharm输出控制显示的设置
        pd.set_option('expand_frame_repr', False)  # True就是可以换行显示。设置成False的时候不允许换行
        pd.set_option('display.max_columns', None)  # 显示所有列
        # pd.set_option('display.max_rows', None)# 显示所有行
        pd.set_option('colheader_justify', 'centre')  # 显示居中

        pro = ts.pro_api('579ffeb73d0ce7893be7c5565ec91f9164e4f70828be7100dc2299ba')
        mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
        mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
        if number[0] == '6':
            df = pro.daily(ts_code=number + '.SH', start_date='20210129', end_date='20210602')
        elif number[0] == '0':
            df = pro.daily(ts_code=number + '.SZ', start_date='20210129', end_date='20210602')

        # df.sort_values(by='trade_date',ascending=False)
        datament = df.loc[:, ['trade_date', 'open', 'close', 'high', 'low', 'vol']]  # ：取所有行数据，后面取date列，open列等数据
        datament = datament.rename(
            columns={'trade_date': 'Date', 'open': 'Open', 'close': 'Close', 'high': 'High', 'low': 'Low',
                     'vol': 'Volume'})  # 更换列名，为后面函数变量做准备
        datament.set_index('Date', inplace=True)  # 设置date列为索引，覆盖原来索引,这个时候索引还是 object 类型，就是字符串类型。
        datament.index = pd.DatetimeIndex(
            datament.index)  # 将object类型转化成 DateIndex 类型，pd.DatetimeIndex 是把某一列进行转换，同时把该列的数据设置为索引 index。
        datament = datament.sort_index(ascending=True)  # 将时间顺序升序，符合时间序列
        mpf.plot(datament, type='candle', mav=(5, 10, 20), volume=True, show_nontrading=False)
# '''
# 将数据导入到mysql数据库中
# '''
        InsertData('wholedata', wholedata)

        i = 0
        while i < len(data):
            InsertData('data', data[i])
            i += 1
        print('成功保存到桌面生成csv文件')
        print('数据成功存储到Mysql数据库')

    def on_listbox(self, event):
        if event.GetString() == '深证':
            s = '选择 深证（股票代码：000001~002946）'
        elif event.GetString() == '上证':
            s = '选择 上证（股票代码：600001~603927）'
        else:
            s = '选择 创业板（股票代码：300001~300999）'
        self.content.SetLabel(s)


class App2(wx.App):

    def OnInit(self):
        # 创建窗口对象
        frame = Frame2()
        frame.Show()
        return True

###登录界面
class Frame1(wx.Frame):
    '''程序主窗口类，继承自wx.Frame'''

    def __init__(self, parent):
        '''构造函数'''

        wx.Frame.__init__(self, parent, -1, '股票查询系统——登录界面')
        self.SetBackgroundColour(wx.Colour(1000, 1000, 1000))
        self.SetSize((520, 220))
        self.Center()
        wx.StaticText(self, -1, u'用户名：', pos=(40, 50), size=(100, -1), style=wx.ALIGN_RIGHT)
        wx.StaticText(self, -1, u'密码：', pos=(40, 80), size=(100, -1), style=wx.ALIGN_RIGHT)
        self.tip = wx.StaticText(self, -1, u'', pos=(145, 110), size=(150, -1), style=wx.ST_NO_AUTORESIZE)
        self.tc1 = wx.TextCtrl(self, -1, '', pos=(145, 50), size=(150, -1), name='TC01', style=wx.TE_CENTER)
        self.tc2 = wx.TextCtrl(self, -1, '', pos=(145, 80), size=(150, -1), name='TC02', style=wx.TE_PASSWORD | wx.TE_CENTER)
        btn_mea = wx.Button(self, -1, u'登录', pos=(350, 50), size=(100, 25))
        # btn_meb = wx.Button(self, -1, u'鼠标所有事件', pos=(350, 80), size=(100, 25))
        btn_close = wx.Button(self, -1, u'关闭窗口', pos=(350, 80), size=(100, 25))
    # 控件事件
        self.tc1.Bind(wx.EVT_TEXT, self.EvtText)
        self.tc2.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_BUTTON, self.OnClose, btn_close)
    # 鼠标事件
        btn_mea.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)         #左键按下
        btn_mea.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)             #左键弹起
        # btn_mea.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        # btn_meb.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)             #左键弹起
    # 键盘事件
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    # 系统事件
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.On_size)
        # self.Bind(wx.EVT_PAINT, self.On_paint)
        # self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
    def EvtText(self, evt):
        '''输入框事件函数'''

        obj = evt.GetEventObject()

    def On_size(self, evt):
        '''改变窗口大小事件函数'''

        self.Refresh()
        evt.Skip()  # 体会作用

    def OnClose(self, evt):
        '''关闭窗口事件函数'''

        dlg = wx.MessageDialog(None, u'确定要关闭本窗口？', u'操作提示', wx.YES_NO | wx.ICON_QUESTION)
        if (dlg.ShowModal() == wx.ID_YES):
            self.Destroy()

    def OnLeftDown(self, evt):
        '''左键按下事件函数'''

        # self.tip.SetLabel(u'左键按下')

    def OnLeftUp(self, evt):
        '''左键弹起事件函数'''

        # self.tip.SetLabel(u'左键弹起')
        if self.tc1.GetValue() == 'W_Java' and self.tc2.GetValue() == '123456':
            print('登录成功')
            self.Destroy()
            app = App2()
            app.MainLoop()
        else:
            dlg = wx.MessageDialog(None, u'用户名不存在或密码错误\n是否重新输入？', u'操作提示', wx.YES_NO | wx.ICON_QUESTION)
            if (dlg.ShowModal() == wx.ID_NO):
                self.Destroy()

    def OnMouseWheel(self, evt):
        '''鼠标滚轮事件函数'''

        vector = evt.GetWheelRotation()
        self.tip.SetLabel(str(vector))

    def OnMouse(self, evt):
        '''鼠标事件函数'''

        self.tip.SetLabel(str(evt.EventType))

    def OnKeyDown(self, evt):
        '''键盘事件函数'''

        key = evt.GetKeyCode()
        self.tip.SetLabel(str(key))


class App1(wx.App):
    def OnInit(self):
        self.SetAppName('股票查询系统——登录界面')
        self.Frame = Frame1(None)
        self.Frame.Show()
        return True

if __name__ == '__main__':
    app = App1()
    app.MainLoop()