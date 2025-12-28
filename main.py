#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF手机App - 独立版
可在手机上独立运行，不需要电脑
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
import os
import json
import pandas as pd
from datetime import datetime
import sqlite3
import threading
import traceback

# 设置窗口大小（手机尺寸）
Window.size = (360, 640)

class ETF手机App(App):
    def build(self):
        self.title = "📱 ETF手机App"
        
        # 主布局
        self.main_layout = TabbedPanel(do_default_tab=False)
        
        # 首页
        首页 = TabbedPanelItem(text='首页')
        首页.add_widget(self.创建首页())
        self.main_layout.add_widget(首页)
        
        # 查看数据
        查看数据 = TabbedPanelItem(text='查看数据')
        查看数据.add_widget(self.创建查看数据页())
        self.main_layout.add_widget(查看数据)
        
        # 上传文件
        上传文件 = TabbedPanelItem(text='上传文件')
        上传文件.add_widget(self.创建上传文件页())
        self.main_layout.add_widget(上传文件)
        
        # 系统设置
        系统设置 = TabbedPanelItem(text='设置')
        系统设置.add_widget(self.创建设置页())
        self.main_layout.add_widget(系统设置)
        
        return self.main_layout
    
    def 创建首页(self):
        """创建首页"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # 标题
        标题 = Label(
            text='📱 ETF手机App',
            font_size=24,
            size_hint=(1, 0.2),
            color=(0.2, 0.4, 0.8, 1)
        )
        layout.add_widget(标题)
        
        # 状态
        self.状态标签 = Label(
            text='状态: 正在初始化...',
            font_size=16,
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.状态标签)
        
        # 统计信息
        统计布局 = GridLayout(cols=2, spacing=10, size_hint=(1, 0.3))
        
        self.etf数量标签 = Label(text='ETF: 0', font_size=18)
        self.股票数量标签 = Label(text='股票: 0', font_size=18)
        self.数据天数标签 = Label(text='天数: 0', font_size=18)
        self.最新日期标签 = Label(text='日期: 无', font_size=18)
        
        统计布局.add_widget(self.etf数量标签)
        统计布局.add_widget(self.股票数量标签)
        统计布局.add_widget(self.数据天数标签)
        统计布局.add_widget(self.最新日期标签)
        
        layout.add_widget(统计布局)
        
        # 功能按钮
        按钮布局 = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.4))
        
        按钮列表 = [
            ('📊 查看持仓数据', self.打开查看数据),
            ('📤 上传Excel文件', self.打开上传文件),
            ('🔄 刷新数据', self.刷新数据),
            ('📁 打开数据文件夹', self.打开数据文件夹)
        ]
        
        for 文本, 回调 in 按钮列表:
            按钮 = Button(
                text=文本,
                size_hint=(1, 0.2),
                background_color=(0.2, 0.6, 0.8, 1)
            )
            按钮.bind(on_press=回调)
            按钮布局.add_widget(按钮)
        
        layout.add_widget(按钮布局)
        
        # 初始化
        Clock.schedule_once(lambda dt: self.初始化应用(), 1)
        
        return layout
    
    def 创建查看数据页(self):
        """创建查看数据页面"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        标题 = Label(text='📊 查看持仓数据', font_size=20, size_hint=(1, 0.1))
        layout.add_widget(标题)
        
        # 筛选条件
        筛选布局 = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        
        self.etf选择 = TextInput(
            hint_text='输入ETF代码 (如512980)',
            size_hint=(0.7, 1)
        )
        
        查询按钮 = Button(
            text='查询',
            size_hint=(0.3, 1),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        查询按钮.bind(on_press=self.查询数据)
        
        筛选布局.add_widget(self.etf选择)
        筛选布局.add_widget(查询按钮)
        layout.add_widget(筛选布局)
        
        # 数据展示区域
        scroll = ScrollView(size_hint=(1, 0.8))
        
        self.数据容器 = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.数据容器.bind(minimum_height=self.数据容器.setter('height'))
        
        scroll.add_widget(self.数据容器)
        layout.add_widget(scroll)
        
        return layout
    
    def 创建上传文件页(self):
        """创建上传文件页面"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # 标题
        标题 = Label(text='📤 上传Excel文件', font_size=20, size_hint=(1, 0.1))
        layout.add_widget(标题)
        
        # 说明
        说明 = Label(
            text='支持格式: .xlsx, .xls, .csv\n从您的截图识别工具中选择文件',
            font_size=16,
            size_hint=(1, 0.2)
        )
        layout.add_widget(说明)
        
        # 文件选择按钮
        选择文件按钮 = Button(
            text='📁 选择Excel文件',
            size_hint=(1, 0.2),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        选择文件按钮.bind(on_press=self.选择文件)
        layout.add_widget(选择文件按钮)
        
        # 文件信息
        self.文件信息标签 = Label(
            text='未选择文件',
            font_size=14,
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.文件信息标签)
        
        # 进度条
        self.进度条 = ProgressBar(max=100, size_hint=(1, 0.1))
        layout.add_widget(self.进度条)
        self.进度条.value = 0
        
        # 上传按钮
        self.上传按钮 = Button(
            text='开始上传',
            size_hint=(1, 0.2),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        self.上传按钮.bind(on_press=self.上传文件)
        self.上传按钮.disabled = True
        layout.add_widget(self.上传按钮)
        
        # 结果
        self.上传结果标签 = Label(
            text='',
            font_size=14,
            size_hint=(1, 0.2)
        )
        layout.add_widget(self.上传结果标签)
        
        self.当前文件路径 = None
        
        return layout
    
    def 创建设置页(self):
        """创建设置页面"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        标题 = Label(text='⚙️ 系统设置', font_size=20, size_hint=(1, 0.1))
        layout.add_widget(标题)
        
        # 按钮列表
        设置项 = [
            ('🔧 初始化数据库', self.初始化数据库),
            ('🗑️ 清理临时文件', self.清理临时文件),
            ('📁 打开工作目录', self.打开工作目录),
            ('📊 查看数据统计', self.查看数据统计),
            ('🔄 检查更新', self.检查更新),
            ('❓ 使用帮助', self.显示帮助)
        ]
        
        for 文本, 回调 in 设置项:
            按钮 = Button(
                text=文本,
                size_hint=(1, 0.12),
                background_color=(0.4, 0.4, 0.4, 1)
            )
            按钮.bind(on_press=回调)
            layout.add_widget(按钮)
        
        # 版本信息
        版本 = Label(
            text='ETF手机App v1.0\n© 2025',
            font_size=12,
            size_hint=(1, 0.2)
        )
        layout.add_widget(版本)
        
        return layout
    
    def 初始化应用(self):
        """初始化应用"""
        try:
            # 创建必要文件夹
            for 文件夹 in ['data', 'database', 'exports']:
                if not os.path.exists(文件夹):
                    os.makedirs(文件夹)
            
            # 初始化数据库
            self.初始化数据库文件()
            
            # 更新状态
            self.状态标签.text = '状态: 运行正常'
            self.状态标签.color = (0, 0.7, 0, 1)
            
            # 加载统计
            self.刷新数据(None)
            
        except Exception as e:
            self.状态标签.text = f'状态: 错误 - {str(e)}'
            self.状态标签.color = (0.9, 0, 0, 1)
    
    def 初始化数据库文件(self):
        """初始化数据库文件"""
        数据库路径 = 'database/etf_data.db'
        
        if os.path.exists(数据库路径):
            return
        
        conn = sqlite3.connect(数据库路径)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS etf_info (
            etf_code TEXT PRIMARY KEY,
            etf_name TEXT NOT NULL,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS etf_holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            etf_code TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            proportion DECIMAL(6,4),
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def 刷新数据(self, instance):
        """刷新数据"""
        try:
            # 获取统计
            conn = sqlite3.connect('database/etf_data.db')
            cursor = conn.cursor()
            
            # ETF数量
            cursor.execute("SELECT COUNT(DISTINCT etf_code) FROM etf_info")
            etf数量 = cursor.fetchone()[0] or 0
            
            # 股票数量
            cursor.execute("SELECT COUNT(DISTINCT stock_code) FROM etf_holdings")
            股票数量 = cursor.fetchone()[0] or 0
            
            # 数据天数
            cursor.execute("SELECT COUNT(DISTINCT date) FROM etf_holdings")
            数据天数 = cursor.fetchone()[0] or 0
            
            # 最新日期
            cursor.execute("SELECT MAX(date) FROM etf_holdings")
            最新日期 = cursor.fetchone()[0] or "无数据"
            
            conn.close()
            
            # 更新界面
            self.etf数量标签.text = f'ETF: {etf数量}'
            self.股票数量标签.text = f'股票: {股票数量}'
            self.数据天数标签.text = f'天数: {数据天数}'
            self.最新日期标签.text = f'日期: {最新日期}'
            
        except Exception as e:
            print(f"刷新数据失败: {e}")
    
    def 打开查看数据(self, instance):
        """打开查看数据标签"""
        self.main_layout.switch_to(self.main_layout.tab_list[1])
    
    def 打开上传文件(self, instance):
        """打开上传文件标签"""
        self.main_layout.switch_to(self.main_layout.tab_list[2])
    
    def 查询数据(self, instance):
        """查询数据"""
        etf代码 = self.etf选择.text.strip()
        
        if not etf代码:
            self.显示消息("请输入ETF代码")
            return
        
        # 清空现有数据
        self.数据容器.clear_widgets()
        
        try:
            conn = sqlite3.connect('database/etf_data.db')
            cursor = conn.cursor()
            
            # 获取最新日期的持仓
            cursor.execute('''
            SELECT date, stock_code, stock_name, proportion
            FROM etf_holdings
            WHERE etf_code = ?
            ORDER BY date DESC, proportion DESC
            LIMIT 50
            ''', (etf代码,))
            
            数据 = cursor.fetchall()
            conn.close()
            
            if not 数据:
                self.显示消息(f"没有找到ETF {etf代码} 的数据")
                return
            
            # 显示数据
            for 日期, 股票代码, 股票名称, 占比 in 数据:
                项目 = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=40
                )
                
                股票标签 = Label(
                    text=f'{股票代码} {股票名称}',
                    size_hint=(0.7, 1)
                )
                
                占比标签 = Label(
                    text=f'{占比}%',
                    size_hint=(0.3, 1),
                    color=(0, 0.7, 0, 1)
                )
                
                项目.add_widget(股票标签)
                项目.add_widget(占比标签)
                self.数据容器.add_widget(项目)
            
        except Exception as e:
            self.显示消息(f"查询失败: {e}")
    
    def 选择文件(self, instance):
        """选择文件"""
        # 创建文件选择器
        选择器 = FileChooserListView(
            path='.',
            filters=['*.xlsx', '*.xls', '*.csv']
        )
        
        弹窗 = Popup(
            title='选择Excel文件',
            content=选择器,
            size_hint=(0.9, 0.9)
        )
        
        def 选择完成(chooser, selection):
            if selection:
                self.当前文件路径 = selection[0]
                self.文件信息标签.text = f'已选择: {os.path.basename(selection[0])}'
                self.上传按钮.disabled = False
            弹窗.dismiss()
        
        选择器.bind(on_submit=选择完成)
        弹窗.open()
    
    def 上传文件(self, instance):
        """上传文件"""
        if not self.当前文件路径 or not os.path.exists(self.当前文件路径):
            self.显示消息("请先选择文件")
            return
        
        # 禁用按钮
        self.上传按钮.disabled = True
        self.上传按钮.text = '上传中...'
        self.进度条.value = 10
        
        # 在新线程中处理
        thread = threading.Thread(target=self.处理文件上传)
        thread.start()
    
    def 处理文件上传(self):
        """处理文件上传"""
        try:
            # 读取文件
            self.进度条.value = 30
            
            文件路径 = self.当前文件路径
            文件名 = os.path.basename(文件路径)
            
            if 文件名.endswith('.csv'):
                df = pd.read_csv(文件路径, encoding='utf-8')
            else:
                df = pd.read_excel(文件路径)
            
            self.进度条.value = 50
            
            # 连接数据库
            conn = sqlite3.connect('database/etf_data.db')
            cursor = conn.cursor()
            
            # 今天的日期
            今天 = datetime.now().strftime('%Y-%m-%d')
            导入数量 = 0
            
            for _, row in df.iterrows():
                try:
                    # 提取数据
                    etf_code = str(row.get('ETF代码', row.get('ETF_Code', ''))).strip()
                    if not etf_code:
                        continue
                    
                    stock_code = str(row.get('股票代码', row.get('Stock_Code', ''))).strip()
                    if not stock_code:
                        continue
                    
                    stock_name = str(row.get('股票名称', row.get('Stock_Name', ''))).strip()
                    if not stock_name:
                        stock_name = f"股票{stock_code}"
                    
                    # 处理占比
                    proportion = 0.0
                    占比字段 = row.get('市值占比', row.get('占比', row.get('Proportion', 0)))
                    if pd.notna(占比字段):
                        try:
                            prop_str = str(占比字段).replace('%', '').strip()
                            proportion = float(prop_str)
                        except:
                            proportion = 0.0
                    
                    # ETF名称
                    etf_name = str(row.get('ETF名称', row.get('ETF_Name', ''))).strip()
                    if not etf_name:
                        etf_name = f"ETF{etf_code}"
                    
                    # 保存到数据库
                    cursor.execute('''
                    INSERT OR REPLACE INTO etf_info (etf_code, etf_name)
                    VALUES (?, ?)
                    ''', (etf_code, etf_name))
                    
                    cursor.execute('''
                    INSERT OR REPLACE INTO etf_holdings 
                    (date, etf_code, stock_code, stock_name, proportion)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (今天, etf_code, stock_code, stock_name, proportion))
                    
                    导入数量 += 1
                    
                except Exception as e:
                    print(f"处理行失败: {e}")
            
            conn.commit()
            conn.close()
            
            self.进度条.value = 100
            
            # 更新界面
            Clock.schedule_once(lambda dt: self.上传完成(导入数量, 今天), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.上传失败(str(e)), 0)
    
    def 上传完成(self, 数量, 日期):
        """上传完成"""
        self.上传按钮.disabled = False
        self.上传按钮.text = '开始上传'
        
        self.上传结果标签.text = f'✅ 上传成功！\n导入{数量}条记录\n日期: {日期}'
        self.上传结果标签.color = (0, 0.7, 0, 1)
        
        # 刷新统计
        self.刷新数据(None)
        
        # 清空文件选择
        self.当前文件路径 = None
        self.文件信息标签.text = '未选择文件'
        self.进度条.value = 0
    
    def 上传失败(self, 错误信息):
        """上传失败"""
        self.上传按钮.disabled = False
        self.上传按钮.text = '开始上传'
        
        self.上传结果标签.text = f'❌ 上传失败\n{错误信息}'
        self.上传结果标签.color = (0.9, 0, 0, 1)
        self.进度条.value = 0
    
    def 打开数据文件夹(self, instance):
        """打开数据文件夹"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile('data')
            elif os.name == 'posix':  # Linux/Mac
                os.system('open data' if sys.platform == 'darwin' else 'xdg-open data')
        except:
            self.显示消息("无法打开文件夹")
    
    def 打开工作目录(self, instance):
        """打开工作目录"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile('.')
            elif os.name == 'posix':  # Linux/Mac
                os.system('open .' if sys.platform == 'darwin' else 'xdg-open .')
        except:
            self.显示消息("无法打开目录")
    
    def 初始化数据库(self, instance):
        """初始化数据库"""
        try:
            if os.path.exists('database/etf_data.db'):
                os.remove('database/etf_data.db')
            
            self.初始化数据库文件()
            self.显示消息("数据库初始化完成")
            self.刷新数据(None)
        except Exception as e:
            self.显示消息(f"初始化失败: {e}")
    
    def 清理临时文件(self, instance):
        """清理临时文件"""
        try:
            for 文件 in os.listdir('.'):
                if 文件.endswith('.tmp') or 文件.endswith('.log'):
                    os.remove(文件)
            
            self.显示消息("临时文件清理完成")
        except Exception as e:
            self.显示消息(f"清理失败: {e}")
    
    def 查看数据统计(self, instance):
        """查看数据统计"""
        try:
            conn = sqlite3.connect('database/etf_data.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM etf_info")
            etf数量 = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM etf_holdings")
            持仓数量 = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT DISTINCT date FROM etf_holdings ORDER BY date DESC")
            日期列表 = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            消息 = f"ETF数量: {etf数量}\n持仓记录: {持仓数量}\n数据日期: {len(日期列表)}天"
            
            if 日期列表:
                消息 += f"\n最新日期: {日期列表[0]}"
            
            self.显示消息(消息)
            
        except Exception as e:
            self.显示消息(f"获取统计失败: {e}")
    
    def 检查更新(self, instance):
        """检查更新"""
        self.显示消息("当前版本: v1.0\n已是最新版本")
    
    def 显示帮助(self, instance):
        """显示帮助"""
        帮助文本 = """📱 ETF手机App 使用帮助

主要功能:
1. 上传Excel文件 - 支持.xlsx/.xls/.csv格式
2. 查看持仓数据 - 输入ETF代码查询
3. 本地数据存储 - 不需要网络连接

使用流程:
1. 在电脑上用截图识别工具生成Excel
2. 将Excel文件复制到手机
3. 在App中选择文件上传
4. 查看数据

数据格式要求:
- ETF代码 (必需)
- 股票代码 (必需)
- 股票名称 (可选)
- 市值占比 (必需)"""
        
        self.显示消息(帮助文本)
    
    def 显示消息(self, 消息):
        """显示消息弹窗"""
        弹窗 = Popup(
            title='消息',
            content=Label(text=消息),
            size_hint=(0.8, 0.6)
        )
        弹窗.open()

if __name__ == '__main__':
    ETF手机App().run()