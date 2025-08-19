"""
Date utility functions.
日期工具类
"""
from datetime import datetime
import locale
import platform


class DateUtil:
    """Utility class for date operations."""
    
    @staticmethod
    def current_date_info() -> str:
        """
        Get current date information in Chinese format.
        获取当前日期信息
        """
        # Get current date
        current_date = datetime.now()
        
        # Get month and day
        month = current_date.month
        day = current_date.day
        year = current_date.year
        
        # Get day of week in Chinese
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        day_of_week_string = weekdays[current_date.weekday()]
        
        # Format output in Chinese
        formatted_date = f"{year}年{month}月{day}日"
        
        return f"今天是 {formatted_date} {day_of_week_string}"