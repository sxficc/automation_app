import threading
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem
from selenium import webdriver

class RegistrationWorker(QThread):
    update_status = pyqtSignal(int, str)
    reload_table = pyqtSignal()  # 用于通知主线程重新加载表格
    save_configs_signal = pyqtSignal()  # 用于通知主线程保存配置

    def __init__(self, account_table, thread_count, log_callback):
        super().__init__()
        self.account_table = account_table
        self.thread_count = thread_count
        self.log = log_callback
        self.threads = []

    def run(self):
        self.log("注册线程启动...")
        accounts_to_register = self.get_unregistered_accounts()
        self.log(f"找到 {len(accounts_to_register)} 个未注册账号")

        for i, account in enumerate(accounts_to_register):
            thread_name = f"线程{i + 1}"  # 设置线程名称为“线程1、线程2……”等
            thread = threading.Thread(target=self.process_account, args=(i, account, thread_name))
            self.threads.append(thread)
            thread.start()

        for i, thread in enumerate(self.threads):
            thread.join()

        self.log("所有账号注册完成")
        self.save_configs_signal.emit()  # 触发信号保存配置
        self.reload_table.emit()  # 触发信号重新加载表格

    def get_threads(self):
        return self.threads

    def get_unregistered_accounts(self):
        unregistered = []
        for row in range(self.account_table.rowCount()):
            status = self.account_table.item(row, 2).text()
            if status == '未注册':
                email = self.account_table.item(row, 0).text()
                password = self.account_table.item(row, 1).text()
                unregistered.append((row, email, password))
        return unregistered

    def process_account(self, thread_index, account, thread_name):
        row, email, password = account
        browser = self.create_browser_instance()

        try:
            # 执行注册操作
            self.update_status.emit(thread_index, f"{email} - 注册中")
            self.register_account(browser, email, password)
            self.update_status.emit(thread_index, f"{email} - 注册完成")
            self.account_table.setItem(row, 2, QTableWidgetItem("已注册"))
            self.log(f"账号 {email} 注册成功")

            # 模拟加入购物车过程
            self.update_status.emit(thread_index, f"{email} - 加入购物车中")
            self.add_to_cart(browser)
            self.update_status.emit(thread_index, f"{email} - 加入购物车完成")
            self.log(f"账号 {email} 加入购物车完成")

            # 模拟支付过程
            self.update_status.emit(thread_index, f"{email} - 支付中")
            self.process_payment(browser)
            self.update_status.emit(thread_index, f"{email} - 支付完成")
            self.log(f"账号 {email} 支付完成")

        finally:
            browser.quit()

        # 实时保存每次成功操作后的配置
        self.save_configs_signal.emit()

    def create_browser_instance(self):
        # 创建一个新的浏览器实例
        options = webdriver.ChromeOptions()
        # 根据需要配置浏览器选项，例如无头模式、代理等
        # options.add_argument('--headless')
        browser = webdriver.Chrome(options=options)
        return browser

    def register_account(self, browser, email, password):
        # 访问注册页面并进行注册
        browser.get('https://example.com/register')
        email_input = browser.find_element_by_name('email')
        password_input = browser.find_element_by_name('password')
        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_button = browser.find_element_by_name('submit')
        submit_button.click()
        time.sleep(2)  # 等待页面加载完成

    def add_to_cart(self, browser):
        # 模拟加入购物车的操作
        browser.get('https://example.com/product-page')
        add_to_cart_button = browser.find_element_by_name('add_to_cart')
        add_to_cart_button.click()
        time.sleep(2)  # 等待操作完成

    def process_payment(self, browser):
        # 模拟支付的操作
        browser.get('https://example.com/checkout')
        pay_button = browser.find_element_by_name('pay')
        pay_button.click()
        time.sleep(2)  # 等待支付完成
