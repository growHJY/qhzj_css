from src.utils.authorization_decorated import login_authorization_decorator


@login_authorization_decorator("12311")
def aa():
    print("函数本体内容")


aa()
