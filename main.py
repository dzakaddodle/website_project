from database import DatabaseManager, UserManager, StockManager
from users import User
from searcher import StockMarket
from menu import Menu
from flask import Flask, render_template, request, redirect, url_for

db = DatabaseManager()
db.create_tables()
user_manager = UserManager(db)
stock_manager = StockManager(db)


user = User(user_manager)
search = StockMarket(stock_manager, user)

menu = Menu(user, search, user_manager, stock_manager)
while menu.not_logged_in:
    menu.display()
    menu.create_menu()
