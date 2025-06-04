from db.mongodb_manager import usersRepository, adminsRepository
import logging

logger = logging.getLogger("admin_manager")

def add_admin(username: str):
    if adminsRepository.find_one_by_username(username):
        print("该用户已是管理员")
        return
    user = usersRepository.find_one_by_username(username)
    if not user:
        print("用户不存在")
        return
    if adminsRepository.add_admin(user.id, username):
        logger.info(f"添加管理员成功: user_id={user.id}, username={username}")
        print("添加管理员成功")
    else:
        print("添加管理员失败")

def remove_admin(username: str):
    admin = adminsRepository.find_one_by_username(username)
    if not admin:
        print("该用户不是管理员")
        return
    if adminsRepository.remove_admin(admin.user_id):
        logger.info(f"移除管理员成功: user_id={admin.user_id}, username={username}")
        print("移除管理员成功")
    else:
        print("移除管理员失败")

def list_admins():
    for admin in adminsRepository.list_admins():
        print(f"user_id: {admin.user_id}, username: {admin.username}")

def print_help():
    print("可用命令: add 用户名 | remove 用户名 | list | exit")

if __name__ == "__main__":
    print_help()
    while True:
        try:
            cmd = input("请输入命令: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出")
            break
        if not cmd:
            continue
        if cmd == "exit":
            print("退出")
            break
        elif cmd == "list":
            list_admins()
        elif cmd.startswith("add "):
            _, username = cmd.split(" ", 1)
            add_admin(username.strip())
        elif cmd.startswith("remove "):
            _, username = cmd.split(" ", 1)
            remove_admin(username.strip())
        else:
            print("命令无效")
            print_help()