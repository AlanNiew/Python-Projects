import asyncio
import math
import os
import threading
import time
from pathlib import Path
from typing import Optional, Dict
import aiohttp
import ctypes
import tkinter as tk
from tkinter import messagebox

import requests
from PIL import Image, ImageTk
import io

BING_YING_API_URL = "https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&country=CN&locale=zh-CN"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
async def get_wallpaper_info() -> Optional[Dict]:
    """
    从API获取壁纸信息（单次请求，包含URL和描述）
    返回示例:
    {
        "url": "https://example.com/wallpaper.jpg",
        "title": "美丽的风景",
        "description": "黄石公园的日出",
        "copyright": "© 摄影师"
    }
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BING_YING_API_URL, headers=REQUEST_HEADERS, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                print("成功获取壁纸信息:", data)
                ad_data = data.get("ad", {})

                # 提取所有关键信息
                return {
                    "url": ad_data.get("landscapeImage", {}).get("asset"),
                    "title": ad_data.get("title", "未命名壁纸"),
                    "description": ad_data.get("description", "暂无描述"),
                    "copyright": ad_data.get("copyright", "未知作者")
                }

    except Exception as e:
        print(f"获取壁纸信息失败: {str(e)}")
        return None

# def download_wallpaper(url: str, save_path: str) -> Optional[str]:
#     """下载壁纸"""
#     try:
#         # 下载图片
#         print(f"正在下载壁纸: {url}")
#         response = requests.get(url,stream=True)
#         response.raise_for_status()
#
#         # 保存图片
#         with open(save_path, "wb") as f:
#             for chunk in response.iter_content(8192):
#                 f.write(chunk)
#
#         print(f"图片已下载到: {os.path.abspath(save_path)}")
#         return save_path
#
#     except Exception as e:
#         print(f"下载图片失败: {e}")
#         return None


def set_wallpaper_windows(image_path):
    try:
        # 转换为绝对路径
        abs_path = os.path.abspath(image_path)

        # 设置壁纸
        SPI_SETDESKWALLPAPER = 0x0014
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abs_path, 3)
        print(f"壁纸已设置为: {abs_path}")
        return True

    except Exception as e:
        print(f"设置壁纸失败: {e}")
        return False
class WallpaperApp:
    def __init__(self):
        self.quit_button = None
        self.set_button = None
        self.info_text = None
        self.image_label = None
        self.next_button = None
        self.window = tk.Tk()
        self.window.title("必应每日壁纸")
        self.window.geometry("1000x750")
        # 用于存储异步任务
        self.task = None
        self.running = False
        # 当前壁纸信息
        self.current_wallpaper_url = None
        self.current_wallpaper_data = None

        # 创建UI元素
        self.create_widgets()
        # 获取并显示第一张壁纸
        self.start_async_task(runnable=self.fetch_and_show_wallpaper())
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    def create_widgets(self):
        """创建界面元素"""
        # 图片显示区域
        self.image_label = tk.Label(self.window)
        self.image_label.pack(pady=20)

        # 壁纸信息显示
        self.info_text = tk.Text(self.window, height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, padx=20, pady=10)
        self.info_text.config(state=tk.DISABLED)

        # 按钮区域
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)

        self.set_button = tk.Button(
            button_frame,
            text="设为壁纸",
            command=self.set_as_wallpaper,
            state=tk.DISABLED
        )
        self.set_button.pack(side=tk.LEFT, padx=10)

        self.save_button = tk.Button(
            button_frame,
            text="保存图片",
            command=self.save_wallpaper,
            state=tk.DISABLED
        )
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(
            button_frame,
            text="换一张",
            command= lambda: self.start_async_task(self.fetch_and_show_wallpaper)
        )
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.quit_button = tk.Button(
            button_frame,
            text="退出",
            command=self.window.quit
        )
        self.quit_button.pack(side=tk.LEFT, padx=10)

    async def fetch_and_show_wallpaper(self):
        """获取并显示壁纸"""
        self.set_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)

        # 清空当前显示
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "正在获取壁纸...\n")
        self.info_text.config(state=tk.DISABLED)
        self.window.update()

        # 获取壁纸URL
        wallpaper_info = await get_wallpaper_info()
        if not wallpaper_info or not wallpaper_info["url"]:
            messagebox.showerror("错误", "无法获取壁纸链接")
            self.next_button.config(state=tk.NORMAL)
            print("无法获取有效的壁纸信息！")
            return

        self.current_wallpaper_url = wallpaper_info["url"]

        # 下载并显示壁纸
        # save_path = f"wallpaper{int(time.time())}.jpg"
        # wallpaper_photo = download_wallpaper(self.current_wallpaper_url,save_path) //写入文件
        if self.current_wallpaper_data:
            self.current_wallpaper_data.close()
        wallpaper_photo = await self.cache_wallpaper(self.current_wallpaper_url) # 缓存图片
        if not wallpaper_photo:
            messagebox.showerror("错误", "下载壁纸失败")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END,"下载壁纸失败,换一张重试！")
            self.next_button.config(state=tk.NORMAL)
            return
        self.current_wallpaper_data = wallpaper_photo
        self.show_wallpaper_preview(wallpaper_photo)

        # 获取并显示壁纸信息
        self.show_wallpaper_info(wallpaper_info)
        self.set_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)

    def show_wallpaper_preview(self, img_data):
        """显示壁纸预览"""
        try:
            # 从内存中加载图片
            img_data.seek(0)
            # img_data = io.BytesIO(img_data)

            img = Image.open(img_data)

            # 调整大小以适应窗口
            max_size = (800, 600)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 转换为Tkinter可用的格式
            photo = ImageTk.PhotoImage(img)

            # 更新显示
            self.image_label.config(image=photo)
            self.image_label.image = photo  # 保持引用

        except Exception as e:
            print(f"显示壁纸预览失败: {str(e)}")
            messagebox.showerror("错误", "无法显示壁纸预览")

    def show_wallpaper_info(self,info):
        """显示壁纸信息"""
        try:
            # response = requests.get(
            #     "https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&country=CN&locale=zh-CN")
            # data = response.json()
            # info = data.get("ad", {})

            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)

            self.info_text.insert(tk.END, f"标题: {info['title']}\n")
            self.info_text.insert(tk.END, f"描述: {info['description']}\n")
            self.info_text.insert(tk.END, f"版权: {info['copyright']}\n")

            self.info_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"获取壁纸信息失败: {str(e)}")

    async def cache_wallpaper(self,image_url: str):
        """缓存壁纸到内存"""
        """异步缓存壁纸到内存"""
        try:
            print(f"获取壁纸: {image_url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, headers=REQUEST_HEADERS, timeout=30) as response:
                    # 获取响应信息
                    content_length = response.content_length
                    print(f"响应长度: {content_length}")
                    print(f"状态码: {response.status}")
                    response.raise_for_status()

                    # 使用内存中的图片数据
                    img_data = io.BytesIO()
                    count = 1
                    chunk_size = 0
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        chunk_size += len(chunk)
                        img_data.write(chunk)
                        #     展示加载进度
                        if count % 5 ==0:
                            progress = math.ceil((chunk_size / content_length) * 100)
                            self.info_text.config(state=tk.NORMAL)
                            self.info_text.insert(tk.END, f"加载进度: {progress} %\n")
                            self.info_text.see(tk.END) # 滚动到底部
                            self.info_text.config(state=tk.DISABLED)  # 恢复禁用状态
                            self.window.update()
                        count+=1
                    img_data.seek(0)
                    print(f"图片获取成功,大小为: {math.ceil(len(img_data.getvalue()) / 1024)} KB")
                    return img_data

        except Exception as e:
            print(f"下载壁纸失败: {str(e)}")
            return None
    def set_as_wallpaper(self):
        """将当前预览的壁纸设置为桌面背景"""
        if not self.current_wallpaper_data or not self.current_wallpaper_url:
            messagebox.showerror("错误", "没有可设置的壁纸")
            return

        # 确认对话框
        if not messagebox.askyesno("确认", "确定要将此图片设为桌面壁纸吗？"):
            return

        try:
            # 保存到永久位置
            save_dir = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Themes")
            Path(save_dir).mkdir(parents=True, exist_ok=True)

            filename = f"bing_wallpaper.jpg"
            save_path = os.path.join(save_dir, filename)
            # 将内存中的图片数据写入文件
            with open(save_path, "wb") as f:
                self.current_wallpaper_data.seek(0)
                f.write(self.current_wallpaper_data.read())

            # 设置壁纸
            set_wallpaper_windows(save_path)

            messagebox.showinfo("成功", "壁纸设置成功！")
        except Exception as e:
            messagebox.showerror("错误", f"设置壁纸失败: {str(e)}")

    def save_wallpaper(self):
        """保存当前预览的壁纸"""
        if not self.current_wallpaper_data or not self.current_wallpaper_url:
            messagebox.showerror("错误", "没有可保存的壁纸")
            return

        try:
            # 确认对话框
            # if not messagebox.askyesno("确认", "确定要将此图片保存吗？"):
            #     return

            # 将内存中的图片数据写入文件
            file_name = f"wallpaper_{int(time.time())}.jpg"
            save_path = os.path.join(os.getcwd(), file_name)
            with open(save_path, "wb") as f:
                self.current_wallpaper_data.seek(0)
                f.write(self.current_wallpaper_data.read())

            if not save_path:
                messagebox.showerror("错误", "保存失败")
            else:
                messagebox.showinfo("成功", f"壁纸已保存到: {os.path.abspath(save_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def on_close(self):
        if self.current_wallpaper_data:
            self.current_wallpaper_data.close()
        self.window.destroy()
    def start_async_task(self, runnable):
        """启动异步任务（在新线程中运行 asyncio）"""
        if self.running:
            return

        self.running = True

        # 在新线程中运行 asyncio 事件循环
        self.task = threading.Thread(
            target=self.run_async_task,
            args=(runnable,),
            daemon=True
        )
        self.task.start()

    def run_async_task(self,runnable):
        """在新线程中运行 asyncio 任务"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            if asyncio.iscoroutine(runnable):
                loop.run_until_complete(runnable)
            elif callable(runnable):
                # 如果传入的是函数，需要调用它来获取协程对象
                coroutine = runnable()
                if asyncio.iscoroutine(coroutine):
                    loop.run_until_complete(coroutine)
                else:
                    raise TypeError("输入必须是函数或协程对象!")
            else:
                raise TypeError("输入必须是函数或协程对象!")
        finally:
            self.running = False
            loop.close()
if __name__ == "__main__":
    app = WallpaperApp()
    app.window.mainloop()