def split_on_found(s):
    # 寻找不区分大小写的"found"的位置
    index = s.lower().find('found')
    # 如果找到了"found"，则分割字符串
    if index != -1:
        return s[:index], s[index:]
    else:
        return '', s